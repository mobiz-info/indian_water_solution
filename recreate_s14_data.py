import os
import django
import datetime
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import transaction
from accounts.models import Customers
from client_management.models import CustomerSupply, CustomerSupplyItems, CustomerOutstanding, OutstandingAmount, CustomerOutstandingReport
from invoice_management.models import Invoice, InvoiceItems, InvoiceDailyCollection
from sales_management.models import Receipt

ROUTE_NAME = "S-14"
TARGET_DATE = datetime.date(2026, 4, 13)
DO_SAVE = False  # Set to True to actually save to DB

def recreate_s14_data():
    print("=" * 80)
    print(f"🔄 RECREATING OUTSTANDING & INVOICE FOR ROUTE: {ROUTE_NAME} ON {TARGET_DATE}")
    print("Dry Run:", not DO_SAVE)
    print("=" * 80)

    # Get customers in S-14
    customers = Customers.objects.filter(routes__route_name=ROUTE_NAME)
    print(f"Customers found in route {ROUTE_NAME}: {customers.count()}")

    supplies = CustomerSupply.objects.filter(
        customer__in=customers,
        created_date__date=TARGET_DATE
    )
    print(f"Total supplies found on {TARGET_DATE}: {supplies.count()}")

    new_invoices = 0
    new_outstandings = 0

    with transaction.atomic():
        for supply in supplies:
            # Recreate Invoice logic
            if not Invoice.objects.filter(invoice_no=supply.invoice_no).exists() and supply.invoice_no:
                print(f"Restoring Invoice {supply.invoice_no} for Customer {supply.customer.customer_name}")
                if DO_SAVE:
                    invoice = Invoice.objects.create(
                        invoice_no=supply.invoice_no,
                        created_date=supply.created_date,
                        net_taxable=supply.net_payable,
                        vat=supply.vat,
                        discount=supply.discount,
                        amout_total=supply.subtotal,
                        amout_recieved=supply.amount_recieved,
                        customer=supply.customer,
                        reference_no="restored from supply script"
                    )
                    
                    if supply.get_supply_type() == "CREDIT":
                        invoice.invoice_type = "credit_invoice"
                    if invoice.amout_total == invoice.amout_recieved:
                        invoice.invoice_status = "paid"
                    invoice.save()

                    # Recreate InvoiceItems
                    for item in CustomerSupplyItems.objects.filter(customer_supply=supply):
                        InvoiceItems.objects.create(
                            category=item.product.category,
                            product_items=item.product,
                            qty=item.quantity,
                            rate=item.amount,
                            invoice=invoice,
                            remarks='invoice restored from supply items'
                        )
                    
                    # Assume we only recreate what was deleted. 
                    # If Invoice was deleted, maybe InvoiceDailyCollection and Receipt were cascaded? Let's assume they were not.
                    # Wait, Invoice delete cascades on models that have ForeignKey(Invoice, on_delete=models.CASCADE).
                    # InvoiceItems has CASCADE. InvoiceDailyCollection has CASCADE (will check).
                    # Let's recreate InvoiceDailyCollection
                    InvoiceDailyCollection.objects.create(
                        invoice=invoice,
                        created_date=supply.created_date,
                        customer=invoice.customer,
                        salesman=supply.customer.sales_staff,
                        amount=invoice.amout_recieved,
                    )
                new_invoices += 1

            # Only add outstanding for CREDIT supply
            if supply.get_supply_type() == "CREDIT" or supply.amount_recieved < supply.subtotal:
                # Check if outstanding already exists
                if not CustomerOutstanding.objects.filter(customer=supply.customer, invoice_no=supply.invoice_no, created_date__date=TARGET_DATE).exists():
                    balance_amount = supply.subtotal - supply.amount_recieved
                    if balance_amount > 0:
                        print(f"Restoring Outstanding for Customer {supply.customer.customer_name}, Amount: {balance_amount}")
                        if DO_SAVE:
                            customer_outstanding_amount = CustomerOutstanding.objects.create(
                                product_type="amount",
                                created_by=supply.created_by,
                                customer=supply.customer,
                                created_date=supply.created_date,
                                invoice_no=supply.invoice_no
                            )

                            outstanding_amount = OutstandingAmount.objects.create(
                                amount=balance_amount,
                                customer_outstanding=customer_outstanding_amount,
                            )

                            try:
                                outstanding_instance = CustomerOutstandingReport.objects.get(customer=supply.customer, product_type="amount")
                                outstanding_instance.value += Decimal(outstanding_amount.amount)
                                outstanding_instance.save()
                            except CustomerOutstandingReport.DoesNotExist:
                                CustomerOutstandingReport.objects.create(
                                    product_type='amount',
                                    value=outstanding_amount.amount,
                                    customer=outstanding_amount.customer_outstanding.customer
                                )
                        new_outstandings += 1

    print("=" * 80)
    print(f"✅ Invoices to recreate: {new_invoices}")
    print(f"✅ Outstandings to recreate: {new_outstandings}")
    print("=" * 80)

if __name__ == "__main__":
    recreate_s14_data()
