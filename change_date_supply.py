

import os
import django
from django.shortcuts import get_object_or_404


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import F

from accounts.models import Customers
from client_management.models import CustomerOutstanding, CustomerSupply
from invoice_management.models import Invoice
from sales_management.models import CollectionPayment

#from django.utils import timezone
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import F

# 1. Define the range on the 19th that belongs to the 18th
start_range = timezone.make_aware(datetime(2026, 3, 19, 0, 0, 0))
end_range = timezone.make_aware(datetime(2026, 3, 19, 15, 58, 0))

# 2. Identify Customers using the correct field name found in your error log
# Note: Using routes__route_name assuming 'routes' is a ForeignKey to a Route model
# If 'routes' is just a CharField, change this to: routes="S-12D"
customers_on_route = Customers.objects.filter(routes__route_name="S-12D")

if not customers_on_route.exists():
    print("No customers found for Route S-12D. Check if the field name or value is correct.")
else:
    try:
        with transaction.atomic():
            # Common filter for all updates
            target_filter = {"customer__in": customers_on_route}

            # Update Invoices
            inv_count = Invoice.objects.filter(
                **target_filter, 
                invoice_date__range=(start_range, end_range)
            ).update(invoice_date=F('invoice_date') - timedelta(days=1))

            # Update CustomerOutstanding
            out_count = CustomerOutstanding.objects.filter(
                **target_filter, 
                outstanding_date__range=(start_range, end_range)
            ).update(outstanding_date=F('outstanding_date') - timedelta(days=1))

            # Update CustomerSupply
            sup_count = CustomerSupply.objects.filter(
                **target_filter, 
                supply_date__range=(start_range, end_range)
            ).update(supply_date=F('supply_date') - timedelta(days=1))

            # Update CollectionPayment
            pay_count = CollectionPayment.objects.filter(
                **target_filter, 
                created_date__range=(start_range, end_range)
            ).update(created_date=F('created_date') - timedelta(days=1))

            print("Migration Successful:")
            print(f"- Invoices moved: {inv_count}")
            print(f"- Outstanding records moved: {out_count}")
            print(f"- Supplies moved: {sup_count}")
            print(f"- Payments moved: {pay_count}")

    except Exception as e:
        print(f"Error during update: {e}")