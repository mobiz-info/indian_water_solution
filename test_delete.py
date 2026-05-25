import os
import django
import traceback
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sana_water_backend.settings")
django.setup()

from client_management.models import *
from van_management.models import *
from invoice_management.models import *
from sales_management.models import *
from django.db import transaction

# Find one coupon recharge
coupon_recharge = CustomerCoupon.objects.last()
if not coupon_recharge:
    print("No CustomerCoupon found")
    exit()

print(f"Testing delete for coupon recharge ID: {coupon_recharge.pk}")
try:
    with transaction.atomic():
        # Copy the logic from views.py
        if coupon_recharge.balance > 0:
            outstanding_report = CustomerOutstandingReport.objects.get(
                customer=coupon_recharge.customer,
                product_type="amount"
            )
            outstanding_report.value -= Decimal(coupon_recharge.balance)
            outstanding_report.save()

            # delete linked outstanding and amounts
            CustomerOutstanding.objects.filter(
                customer=coupon_recharge.customer,
                product_type="amount"
            ).delete()
            print("Outstanding rolled back")
            
except CustomerOutstandingReport.DoesNotExist:
    print("CustomerOutstandingReport DoesNotExist")
    pass
except Exception as e:
    print(f"EXCEPTION Outstanding: {repr(e)}")
    traceback.print_exc()

try:
    with transaction.atomic():
        coupon_items = CustomerCouponItems.objects.filter(customer_coupon=coupon_recharge)
        for item in coupon_items:
            coupon = item.coupon

            # rollback CustomerCouponStock
            try:
                stock = CustomerCouponStock.objects.get(
                    coupon_method=coupon.coupon_method,
                    customer_id=coupon_recharge.customer.pk,
                    coupon_type_id=coupon.coupon_type_id
                )
                stock.count -= Decimal(coupon.no_of_leaflets)
                stock.save()
                print("CustomerCouponStock rolled back")
            except CustomerCouponStock.DoesNotExist:
                print("CustomerCouponStock DoesNotExist")
                pass

            # rollback VanCouponStock
            try:
                van_stock = VanCouponStock.objects.get(
                    created_date=coupon_recharge.created_date.date(),
                    coupon=coupon
                )
                van_stock.stock += 1
                van_stock.sold_count -= 1
                van_stock.save()
                print("VanCouponStock rolled back")
            except VanCouponStock.DoesNotExist:
                print("VanCouponStock DoesNotExist")
                pass

            # reset coupon stock status
            CouponStock.objects.filter(couponbook=coupon).update(coupon_stock="van")

        print("Deleting coupon_items")
        # coupon_items.delete() # Don't actually delete
except Exception as e:
    print(f"EXCEPTION CouponItems: {repr(e)}")
    traceback.print_exc()

try:
    with transaction.atomic():
        invoice = Invoice.objects.get(invoice_no=coupon_recharge.invoice_no)
        print("Invoice rolled back")
except Invoice.DoesNotExist:
    print("Invoice DoesNotExist")
    pass
except Exception as e:
    print(f"EXCEPTION Invoice: {repr(e)}")
    traceback.print_exc()

try:
    with transaction.atomic():
        receipt = Receipt.objects.get(invoice_number=coupon_recharge.invoice_no)
        print("Receipt rolled back")
except Receipt.DoesNotExist:
    print("Receipt DoesNotExist")
    pass
except Exception as e:
    print(f"EXCEPTION Receipt: {repr(e)}")
    traceback.print_exc()

print("All sections tested!")
