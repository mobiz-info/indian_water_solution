import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
connection.close()

from client_management.models import Customers, CustomerCustodyStock, CustomerOutstandingReport, CustodyCustomItems, OutstandingProduct
from sales_management.models import CustomerSupply
from django.db.models import Sum

customer = Customers.objects.get(custom_id='18142')
print(f"Customer: {customer.customer_name} ({customer.custom_id})")

existing_custody = CustodyCustomItems.objects.filter(
    custody_custom__customer=customer,
    product__product_name__in=["5 Gallon", "5 Gallon Empty Bottle"],
)
print("CustodyCustomItems:")
for c in existing_custody:
    print(f"  ID: {c.id}, Qty: {c.quantity}")

existing_outstanding = OutstandingProduct.objects.filter(
    customer_outstanding__customer=customer,
    customer_outstanding__product_type='emptycan',
)
print("OutstandingProduct:")
for o in existing_outstanding:
    print(f"  ID: {o.id}, Qty: {o.empty_bottle}")

