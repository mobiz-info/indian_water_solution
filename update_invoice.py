
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from client_management.models import CustomerCredit, CustomerOutstanding, CustomerSupply
from invoice_management.models import Invoice
from accounts.models import Customers
from decimal import Decimal
from django.db import transaction
from datetime import date
from django.db.models import F
from accounts.models import Customers, CustomUser
import openpyxl

from collections import defaultdict
from invoice_management.models import Invoice
from django.db import transaction

# group invoices by invoice_no
# invoice_map = defaultdict(list)

# for inv in Invoice.objects.order_by("invoice_no", "id"):
#     invoice_map[inv.invoice_no].append(inv)

# with transaction.atomic():
#     for invoice_no, invoices in invoice_map.items():
#         if len(invoices) > 1:
#             # keep first as-is
#             for index, inv in enumerate(invoices[1:], start=1):
#                 new_invoice_no = f"{invoice_no}-{index}"
#                 inv.invoice_no = new_invoice_no
#                 inv.save(update_fields=["invoice_no"])
#                 print(f"Updated: {invoice_no} → {new_invoice_no}")


from django.db.models import F

# today = date.today()
# outstanding_day = date(2026, 1, 1)   # Jan 1

# qs = CustomerOutstanding.objects.filter(
#     outstanding_date__date=outstanding_day,
#     created_date__date=today,
#     customer__routes__route_name="S3",
#     outstandingamount__amount__lt=0
# )

# print("Records to update:", qs.count())
# print(qs.values("id", "created_by"))

# updated_count = CustomerOutstanding.objects.filter(
#     outstanding_date__date=outstanding_day,
#     created_date__date=today,
#     customer__routes__route_name="S-03",
#     outstandingamount__amount__lt=0   # ✅ from OutstandingAmount model
# ).update(
#     created_by="891"
# )

# TEST_ROUTE_NAME = "test_route2"

# supply_updated = CustomerSupply.objects.filter(
#     supply_date__isnull=True,
# ).update(
#     supply_date=F('created_date')
# )

# invoice_updated = Invoice.objects.filter(
#     invoice_date__isnull=True,
#     # customer__routes__route_name=TEST_ROUTE_NAME
# ).update(
#     invoice_date=F('created_date')
# )

# outstanding_updated = CustomerOutstanding.objects.filter(
#     outstanding_date__isnull=True,
#     # customer__routes__route_name=TEST_ROUTE_NAME
# ).update(
#     outstanding_date=F('created_date')
# )

# print("Updated supply rows:", supply_updated)
# print("Updated invoice rows:", invoice_updated)
# print("Updated outstanding rows:", outstanding_updated)

# from product.models import Staff_IssueOrders
# from van_management.models import Van_Routes
# from client_management.models import CustomerCouponItems

# print("Issues:", Staff_IssueOrders.objects.count())
# print("Issues without van:", Staff_IssueOrders.objects.filter(van__isnull=True).count())
# print("Issues without coupon:", Staff_IssueOrders.objects.filter(coupon_book__isnull=True).count())
# print("Van routes:", Van_Routes.objects.count())
# print("Sales:", CustomerCouponItems.objects.count())

# issue_vans = set(Staff_IssueOrders.objects.values_list('van_id', flat=True))
# mapped_vans = set(Van_Routes.objects.values_list('van_id', flat=True))
# print("Unmapped vans:", issue_vans - mapped_vans)

# issue_coupons = set(Staff_IssueOrders.objects.values_list('coupon_book', flat=True))
# sale_coupons = set(CustomerCouponItems.objects.values_list('coupon', flat=True))
# print("Sold but not issued:", sale_coupons - issue_coupons)





# start_dt = make_aware(datetime(2026, 2, 2, 0, 0, 0))
# end_dt   = make_aware(datetime(2026, 2, 2, 23, 59, 59))

# with transaction.atomic():
#     outstanding_qs = CustomerOutstanding.objects.filter(
#     customer__routes__route_name="S-22"
#     ).update(
#         created_by=str(824)
#     )

# print("Updated outstanding:", outstanding_qs)

# EXCEL_FILE = "S-40.xlsx"
# wb = openpyxl.load_workbook(EXCEL_FILE)
# sheet = wb.active

# for row in sheet.iter_rows(min_row=3, values_only=True):
#     customer_code = row[2]   # Column D
#     name = row[0] 
#     building_name = row[1]           # Column E
#     # price = row[4]           # Column F   # Column G
    

#     if customer_code is None: 
#         continue

#     customer_code = str(customer_code).zfill(4)

    

#     try:
#         customer = Customers.objects.get(custom_id=customer_code)
        
#         print("realname",customer.customer_name)
#         customer.customer_name = name
#         print("excelName",name)
        
#         customer.building_name = building_name
#         # customer.save()

#         print(
#             "Updated",customer_code
#         )

#     except Customers.DoesNotExist:
#          print(f"Customer not found: {customer_code}")
        
              
salesman = CustomUser.objects.get(id=819)

with transaction.atomic():
    updated = Invoice.objects.filter(
        customer__routes__route_name="S-21",
    ).update(
        salesman=salesman
    )

print("Updated invoices:", updated)