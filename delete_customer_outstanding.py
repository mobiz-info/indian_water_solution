import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import transaction
from accounts.models import Customers
from client_management.models import CustomerOutstanding, OutstandingAmount
from sales_management.models import CollectionPayment
from invoice_management.models import Invoice

ROUTE_NAME = "S-45"
DO_DELETE = True   # 🔴 SET FALSE FIRST


def delete_s13_full():

    print("=" * 80)
    print(f"🗑 FULL DELETE FOR ROUTE: {ROUTE_NAME}")
    print("Dry Run:", not DO_DELETE)
    print("=" * 80)

    # Get customers in S-13
    customers = Customers.objects.filter(routes__route_name=ROUTE_NAME)

    print("Customers found:", customers.count())

    outstanding_qs = CustomerOutstanding.objects.filter(customer__in=customers)
    collection_qs = CollectionPayment.objects.filter(customer__in=customers)
    invoice_qs = Invoice.objects.filter(customer__in=customers)

    print("Outstanding:", outstanding_qs.count())
    # print("Collections:", collection_qs.count())
    print("Invoices:", invoice_qs.count())

    if not DO_DELETE:
        print("🟡 DRY RUN ONLY — Nothing deleted")
        return

    with transaction.atomic():

        # Delete collections
        collection_deleted, _ = collection_qs.delete()

        # Delete outstanding child amounts
        OutstandingAmount.objects.filter(
            customer_outstanding__in=outstanding_qs
        ).delete()

        # Delete outstanding master
        outstanding_deleted, _ = outstanding_qs.delete()

        # Delete invoices
        invoice_deleted, _ = invoice_qs.delete()

        print("✅ Collection deleted:", collection_deleted)
        print("✅ Outstanding deleted:", outstanding_deleted)
        print("✅ Invoice deleted:", invoice_deleted)

    print("=" * 80)
    print("🚀 S-13 FULL DELETE COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    delete_s13_full()
