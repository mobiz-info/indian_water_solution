from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from accounts.models import CustomUser
from client_management.models import CustomerCredit
from invoice_management.models import Invoice


def get_customer_outstanding_amount(customer, salesman=None):
    salesman = salesman or customer.sales_staff

    invoice_filters = {
        "customer": customer,
        "is_deleted": False,
    }
    credit_filters = {
        "customer": customer,
    }

    if salesman:
        invoice_filters["salesman"] = salesman
        credit_filters["salesman"] = salesman

    invoice_total = Invoice.objects.filter(**invoice_filters).aggregate(
        total=Sum(
            ExpressionWrapper(
                F("amout_total") - F("amout_recieved"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")

    customer_credit = (
        CustomerCredit.objects
        .filter(**credit_filters)
        .aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )

    final_outstanding = invoice_total - customer_credit

    return final_outstanding

def get_salesman_from_customer(customer):
    return CustomUser.objects.filter(
        route=customer.routes
    ).first()
