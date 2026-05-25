import os
import django
from datetime import datetime
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from client_management.models import CustomerOutstanding, OutstandingAmount
from invoice_management.models import Invoice
from sales_management.models import CustomerSupply
from van_management.models import Van_Routes

ROUTE_NAME = "S-14"
OUT_DATE = datetime.strptime("14-04-2026", "%d-%m-%Y")
DO_UPDATE = True   # ✅ KEEP FALSE FIRST


def rebuild_credit_outstanding():
    print("=" * 100)
    print("🔁 REBUILD OUTSTANDING + INVOICE")
    print(f"📍 Route : {ROUTE_NAME}")
    print(f"📅 Date  : {OUT_DATE.date()}")
    print("Dry Run :", not DO_UPDATE)
    print("=" * 100)

    supplies = CustomerSupply.objects.filter(
        customer__routes__route_name=ROUTE_NAME,
        supply_date__date=OUT_DATE.date(),
        amount_recieved=0   # ✅ ONLY FULL CREDIT SALES
    ).select_related("customer")

    print(f"✅ Full credit supplies found: {supplies.count()}")

    for supply in supplies:
        customer = supply.customer
        adjustment = supply.net_payable

        print(
            f"Customer {customer.custom_id} | "
            f"{customer.customer_name} | "
            f"Supply Inv: {supply.invoice_no} | "
            f"Amount: {adjustment}"
        )

        if adjustment <= 0:
            print("  ➖ Skipped zero amount")
            continue

        if not DO_UPDATE:
            continue

        with transaction.atomic():
            route = customer.routes
            van_route = (
                Van_Routes.objects
                .filter(routes=route)
                .select_related("van__salesman")
                .first()
            )

            salesman = van_route.van.salesman if van_route else None

            # Prevent duplicate restore
            already_exists = CustomerOutstanding.objects.filter(
                customer=customer,
                outstanding_date=OUT_DATE,
            ).exists()

            if already_exists:
                print("  ♻️ Outstanding already exists")
                continue

            # -----------------------------
            # 1) Outstanding master
            # -----------------------------
            outstanding = CustomerOutstanding.objects.create(
                customer=customer,
                product_type="amount",
                created_date=OUT_DATE,
                outstanding_date=OUT_DATE,
                created_by=str(salesman.id) if salesman else ""
            )

            # -----------------------------
            # 2) Outstanding child
            # -----------------------------
            OutstandingAmount.objects.create(
                customer_outstanding=outstanding,
                amount=adjustment
            )

            # -----------------------------
            # 3) Invoice create
            # -----------------------------
            invoice = Invoice.objects.create(
                created_date=OUT_DATE,
                invoice_date=OUT_DATE,
                net_taxable=adjustment,
                vat=0,
                discount=0,
                amout_total=adjustment,
                amout_recieved=0,
                customer=customer,
                reference_no=supply.invoice_no or "supply recovery",
                salesman=salesman,
                invoice_type="credit_invoice",
                invoice_status="non_paid"
            )

            # -----------------------------
            # 4) Link invoice no
            # -----------------------------
            outstanding.invoice_no = invoice.invoice_no
            outstanding.save(update_fields=["invoice_no"])

            # -----------------------------
            # 5) Mark restored
            # -----------------------------
            supply.outstanding_amount_added = True
            supply.save(update_fields=["outstanding_amount_added"])

            print(f"  ✅ Restored -> {invoice.invoice_no}")

    print("=" * 100)
    print("🚀 RECOVERY FINISHED")
    print("=" * 100)


if __name__ == "__main__":
    rebuild_credit_outstanding()