
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
import openpyxl
from decimal import Decimal, InvalidOperation
from django.db import transaction
from accounts.models import Customers
from client_management.models import CustomerCredit



def safe_decimal(value):
    """
    Safely convert any value to Decimal.
    Returns None if invalid.
    """
    if value is None:
        return None

    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))

    value = str(value).strip()

    if value in ("", "-", "—"):
        return None

    # remove thousand separators
    value = value.replace(",", "")

    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def import_customer_credit_from_excel(excel_path):
    """
    Reads Excel and inserts customer credit for NEGATIVE outstanding values only.
    """

    wb = openpyxl.load_workbook(excel_path)
    sheet = wb.active

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for row in sheet.iter_rows(min_row=2, values_only=True):

            # -----------------------------
            # 1️⃣ Customer Code Safe Check
            # -----------------------------
            if row[4] is None:
                skipped_count += 1
                continue

            customer_code = str(row[4]).strip()

            # -----------------------------
            # 2️⃣ Outstanding Safe Convert
            # -----------------------------
            outstanding_raw = row[7]
            outstanding_amount = safe_decimal(outstanding_raw)

            if outstanding_amount is None:
                skipped_count += 1
                continue

            # -----------------------------
            # 3️⃣ Only Negative = Credit
            # -----------------------------
            if outstanding_amount >= 0:
                skipped_count += 1
                continue

            # -----------------------------
            # 4️⃣ Find Customer
            # -----------------------------
            customer = Customers.objects.filter(
                custom_id=customer_code
            ).first()

            if not customer:
                print(f"❌ Customer not found: {customer_code}")
                skipped_count += 1
                continue

            # -----------------------------
            # 5️⃣ Create Credit Entry
            # -----------------------------
            credit_amount = abs(outstanding_amount)

            CustomerCredit.objects.create(
                customer=customer,
                amount=credit_amount,
                source="excel_import",
                remark="Imported customer credit from Excel",
                salesman=customer.sales_staff,
            )

            created_count += 1
            print(
                f"✔ Credit added | Customer {customer_code} | Amount {credit_amount}"
            )

    print("\n--- IMPORT SUMMARY ---")
    print("Credits created :", created_count)
    print("Rows skipped    :", skipped_count)


# 🔥 Run Import
# import_customer_credit_from_excel(
#     "S-36 ROUTE OUTSTANDING UPTO 14-FEB-26 (1).xlsx"
# )
