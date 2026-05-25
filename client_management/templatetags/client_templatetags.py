from datetime import datetime, timedelta, date
from decimal import Decimal
from django.utils import timezone

from django import template
from django.db.models import Q, Sum, F, Case, When, IntegerField

from accounts.models import Customers
from apiservices.serializers import CouponLeafSerializer, FreeLeafletSerializer
from client_management.models import *
from sales_management.models import *

register = template.Library()

@register.simple_tag
def route_wise_bottle_count(route_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__routes__pk=route_pk, product__product_name="5 Gallon")
    
    bottle_supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    bottle_to_custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    bottle_to_paid = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_paid'))['total_quantity'] or 0
    
    foc_supply = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_free'))['total_quantity'] or 0
    empty_bottle_collected = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__collected_empty_bottle'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__routes__pk=route_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__routes__pk=route_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(((bottle_supplied - bottle_to_custody - bottle_to_paid) + foc_supply) - empty_bottle_collected)
    custody_qty = abs(custody_quantity - custody_return)
    
    return supply_qty + custody_qty


@register.simple_tag
def route_wise_customer_bottle_count(customer_pk):
    customer_supply_items = CustomerSupplyItems.objects.filter(customer_supply__customer__pk=customer_pk, product__product_name="5 Gallon")
    
    bottle_supplied = customer_supply_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    bottle_to_custody = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_custody'))['total_quantity'] or 0
    bottle_to_paid = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_paid'))['total_quantity'] or 0
    
    foc_supply = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__allocate_bottle_to_free'))['total_quantity'] or 0
    empty_bottle_collected = customer_supply_items.aggregate(total_quantity=Sum('customer_supply__collected_empty_bottle'))['total_quantity'] or 0
    
    custody_quantity = CustodyCustomItems.objects.filter(custody_custom__customer__pk=customer_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    custody_return = CustomerReturnItems.objects.filter(customer_return__customer__pk=customer_pk, product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    supply_qty = abs(((bottle_supplied - bottle_to_custody - bottle_to_paid) + foc_supply) - empty_bottle_collected)
    custody_qty = abs(custody_quantity - custody_return)
    
    return {
        'supply_qty': supply_qty,
        'custody_qty': custody_qty,
        'total_bottle_count': supply_qty + custody_qty,
    }
        
        
@register.simple_tag
def get_outstanding_amount(customer_id, date, salesman_id=None):
    if not customer_id:
        return Decimal("0.00")

    # -------------------- OUTSTANDING --------------------
    outstanding_qs = OutstandingAmount.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__date__lte=date
    )

    if salesman_id:
            outstanding_qs = outstanding_qs.filter(
                customer_outstanding__created_by=salesman_id
            )

    outstanding_amount = outstanding_qs.aggregate(
        total=Sum('amount')
    )['total'] or Decimal("0.00")

    # -------------------- COLLECTION --------------------
    collection_qs = CollectionPayment.objects.filter(
        customer__pk=customer_id,
        created_date__date__lte=date
    )

    if salesman_id:
        collection_qs = collection_qs.filter(salesman_id=salesman_id)

    collection_amount = collection_qs.aggregate(
        total=Sum('amount_received')
    )['total'] or Decimal("0.00")

    # -------------------- NET --------------------
    return outstanding_amount - collection_amount
    # if outstanding_amounts > collection_amount:
    # else:
    #     return collection_amount - outstanding_amounts

@register.simple_tag
def get_outstanding_bottles(customer_id, date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_bottles = OutstandingProduct.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__lte=date
    ).aggregate(total_bottles=Sum('empty_bottle'))['total_bottles'] or 0
    return outstanding_bottles

@register.simple_tag
def get_outstanding_coupons(customer_id, date):
    if not customer_id:  # Ensure customer_id is not empty
        return 0 
    outstanding_coupons = OutstandingCoupon.objects.filter(
        customer_outstanding__customer__pk=customer_id,
        customer_outstanding__created_date__lte=date,
    ).aggregate(total_coupons=Sum('count'))
    
    return outstanding_coupons.get('total_coupons') or 0


@register.simple_tag
def get_customer_coupon_leafs(customer_id):
    leafs = {}
    coupon_ids_queryset = CustomerCouponItems.objects.filter(customer_coupon__customer_id=customer_id).values_list('coupon__pk', flat=True)
    
    coupon_leafs = CouponLeaflet.objects.filter(used=False,coupon__pk__in=list(coupon_ids_queryset)).order_by("leaflet_name")
    coupon_leafs_data = CouponLeafSerializer(coupon_leafs, many=True).data
    
    free_leafs = FreeLeaflet.objects.filter(used=False,coupon__pk__in=list(coupon_ids_queryset)).order_by("leaflet_name")
    free_leafs_data = FreeLeafletSerializer(free_leafs, many=True).data
    
    leafs = coupon_leafs_data + free_leafs_data
    return leafs

@register.simple_tag
def get_customer_outstanding_aging(route=None, salesman_id=None):
    if not route:
        return []

    # 1. Fetch all relevant data in bulk
    # Get all customers on the route
    customers = Customers.objects.filter(routes__route_name=route)
    customer_ids = list(customers.values_list('pk', flat=True))

    # Get all outstanding entries for these customers, ordered by date (oldest    # Get all outstanding entries for these customers, ordered by date (oldest first)
    # We need individual entries to bucket them correctly after net-off
    outstanding_filter = {
        'customer_outstanding__customer__pk__in': customer_ids
    }
    
    if salesman_id:
        outstanding_filter['customer_outstanding__created_by'] = salesman_id

    all_outstanding = OutstandingAmount.objects.filter(
        **outstanding_filter
    ).values(
        'customer_outstanding__customer__pk',
        'customer_outstanding__customer__customer_name',
        'amount',
        'customer_outstanding__created_date'
    ).order_by('customer_outstanding__created_date')

    # Get total collections per customer
    collection_filter = {
        'customer__pk__in': customer_ids
    }

    if salesman_id:
        collection_filter['salesman_id'] = salesman_id

    all_collections = CollectionPayment.objects.filter(
        **collection_filter
    ).values('customer__pk').annotate(
        total_collected=Sum('amount_received')
    )
    
    # Map collections to customer_id for easy lookup
    collections_map = {item['customer__pk']: item['total_collected'] or 0 for item in all_collections}

    # Group outstanding by customer
    customer_outstanding_map = {}
    for entry in all_outstanding:
        c_id = entry['customer_outstanding__customer__pk']
        if c_id not in customer_outstanding_map:
            customer_outstanding_map[c_id] = {
                'name': entry['customer_outstanding__customer__customer_name'],
                'entries': []
            }
        customer_outstanding_map[c_id]['entries'].append(entry)

    aging_report = []
    current_date = datetime.now().date()

    # 2. Process each customer
    # We must iterate over ALL customers in the route to match customer_outstanding_list
    for c_id in customer_ids:
        # Get customer details (name) - we need to fetch this if not in customer_outstanding_map
        # Optimization: We can create a map of id -> name for all customers first
        # But we already have 'customers' queryset. Let's make a map.
        pass 
    
    # Let's rebuild the loop to iterate over all customers
    customer_map = {c.pk: c.customer_name for c in customers}

    for c_id, c_name in customer_map.items():
        total_collected = collections_map.get(c_id, 0)
        
        # Get outstanding entries if any
        data = customer_outstanding_map.get(c_id)
        outstanding_entries = data['entries'] if data else []

        # Calculate Total Outstanding
        total_outstanding = sum(e['amount'] for e in outstanding_entries)
        
        # Net Balance
        net_balance = total_outstanding - total_collected

        # Buckets
        buckets = {
            'less_than_30': Decimal(0),
            'between_31_and_60': Decimal(0),
            'between_61_and_90': Decimal(0),
            'between_91_and_150': Decimal(0),
            'between_151_and_365': Decimal(0),
            'more_than_365': Decimal(0),
        }

        if net_balance == 0:
            continue
            
        if net_balance < 0:
            # Case: Advance Payment (Negative Balance)
            buckets['less_than_30'] = net_balance
            
            # Add to report
            row = {
                'customer_id': c_id,
                'customer_name': c_name,
                'grand_total': net_balance,
                **buckets
            }
            aging_report.append(row)
            continue

        # Case: Positive Balance (Logic from before)
        
        # We need to remove `total_collected` amount from `outstanding_entries` starting from index 0 (oldest).
        
        remaining_entries = []
        amount_to_knock_off = total_collected

        for entry in outstanding_entries:
            amount = entry['amount']
            if amount_to_knock_off >= amount:
                # Fully generated by collection
                amount_to_knock_off -= amount
                continue # This entry is paid off
            else:
                # Partially paid
                remaining_amount = amount - amount_to_knock_off
                amount_to_knock_off = 0
                # Create a new entry with the remaining amount, keeping the original date
                new_entry = entry.copy()
                new_entry['amount'] = remaining_amount
                remaining_entries.append(new_entry)
        
        for entry in remaining_entries:
            # Check if created_date is datetime or date
            c_date = entry['customer_outstanding__created_date']
            if isinstance(c_date, datetime):
                c_date = c_date.date()
                
            delta = (current_date - c_date).days
            amount = entry['amount']

            if delta <= 30:
                buckets['less_than_30'] += amount
            elif 31 <= delta <= 60:
                buckets['between_31_and_60'] += amount
            elif 61 <= delta <= 90:
                buckets['between_61_and_90'] += amount
            elif 91 <= delta <= 150:
                buckets['between_91_and_150'] += amount
            elif 151 <= delta <= 365:
                buckets['between_151_and_365'] += amount
            else:
                buckets['more_than_365'] += amount

        # Add to report
        row = {
            'customer_id': c_id,
            'customer_name': c_name,
            'grand_total': net_balance, # Should match sum of buckets
            **buckets
        }
        aging_report.append(row)

    return aging_report


@register.simple_tag
def get_customer_wise_outstanding_details(customer, closing_date, to_date):
    
    opening_amount = OutstandingAmount.objects.filter(customer_outstanding__customer__pk=customer, customer_outstanding__created_date__date__lte=closing_date).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    opening_collection = CollectionPayment.objects.filter(customer__pk=customer, created_date__date__lte=closing_date).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
    
    opening_amount = opening_amount - opening_collection
    
    collection_upto = CollectionPayment.objects.filter(customer__pk=customer, created_date__date__gt=closing_date, created_date__date__lt=to_date).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
    
    return{
        "opening_amount": opening_amount,
        "collection_upto": collection_upto,
        "balance_amount": opening_amount - collection_upto,
    }