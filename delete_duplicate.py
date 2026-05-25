import os
import django
from collections import defaultdict
from django.utils import timezone
from datetime import datetime


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from client_management.models import CustomerOutstanding, OutstandingAmount
from invoice_management.models import Invoice

ROUTE_NAME = "S-45"
DO_DELETE = True   # ✅ first False
TARGET_DATE = datetime.strptime("14-04-2026", "%d-%m-%Y").date()

def delete_s14_duplicate_outstanding():
    print("=" * 100)
    print("🚀 STARTING S-14 DUPLICATE CLEANUP")
    print(f"📍 Route: {ROUTE_NAME}")
    print(f"🧪 Dry Run: {not DO_DELETE}")
    print("=" * 100)

    grouped = defaultdict(list)

    print("🔍 Fetching outstanding rows...")
    rows = (
        CustomerOutstanding.objects
        .filter(
            product_type="amount",
            customer__routes__route_name=ROUTE_NAME,
            outstanding_date__date=TARGET_DATE
        )
        .select_related("customer")
        .order_by("created_date")
    )

    print(f"✅ Total outstanding rows fetched: {rows.count()}")

    for out in rows:
        print("-" * 80)
        print(f"📄 Processing outstanding: {out.id}")
        print(f"👤 Customer: {out.customer.custom_id} - {out.customer.customer_name}")

        amount_obj = OutstandingAmount.objects.filter(
            customer_outstanding=out
        ).first()

        if not amount_obj:
            print("⚠️ No OutstandingAmount found, skipped")
            continue

        if not out.outstanding_date:
            print("⚠️ No outstanding date, skipped")
            continue

        # UTC → IST
        local_date = timezone.localtime(out.outstanding_date).date()

        print(f"📅 Local Date: {local_date}")
        print(f"💰 Amount: {amount_obj.amount}")

        key = (
            out.customer.custom_id,
            local_date,
            amount_obj.amount
        )

        print(f"🗂 Group Key: {key}")

        grouped[key].append(out)

    print("=" * 100)
    print(f"📦 Total grouped duplicate keys: {len(grouped)}")
    print("=" * 100)

    for key, records in grouped.items():
        print(f"🔎 Checking key: {key} -> Records: {len(records)}")

        if len(records) <= 1:
            continue

        print(
            f"🔁 Duplicate found | "
            f"Customer: {key[0]} | "
            f"Date: {key[1]} | "
            f"Amount: {key[2]} | "
            f"Delete: {len(records)-1}"
        )

        if not DO_DELETE:
            print("🧪 Dry run mode, skipping delete")
            continue

        # keep oldest, delete rest
        for dup_out in records[1:]:
            print(f"🗑 Preparing delete: {dup_out.id}")

            if dup_out.invoice_no:
                deleted_invoice, _ = Invoice.objects.filter(
                    invoice_no=dup_out.invoice_no
                ).delete()

                print(
                    f"🧾 Invoice delete: {dup_out.invoice_no} "
                    f"({deleted_invoice})"
                )

            dup_out.delete()
            print(f"🗑 Deleted outstanding {dup_out.id}")

    print("=" * 100)
    print("✅ S-14 duplicate cleanup finished")
    print("=" * 100)


if __name__ == "__main__":
    delete_s14_duplicate_outstanding()