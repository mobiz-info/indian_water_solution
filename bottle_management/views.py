from django.forms import ValidationError
from django.shortcuts import render
from datetime import datetime
from django.db import transaction
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from product.models import ProdutItemMaster
from .models import Product, Bottle
import json
import re

from bottle_management.models import Bottle, BottleLedger

# Create your views here.

def get_last_number(date_str, prefix):
    regex = rf"^{date_str}-{prefix}(\d+)$"
    last = (
        Bottle.objects
        .filter(serial_number__regex=regex)
        .order_by("-serial_number")
        .first()
    )
    if not last:
        return 999
    return int(re.search(r"(\d+)$", last.serial_number).group(1))

@transaction.atomic
def generate_bottles(
    *,
    product,
    quantity,
    prefix="BTL",
    created_by=None
):
    """
    Generates bottles with serial numbers
    """

    today = datetime.now()
    date_str = today.strftime("%d-%m")

    last_number = get_last_number(prefix, date_str)

    bottles = []
    ledgers = []

    for i in range(1, quantity + 1):
        serial = f"{date_str}-{prefix}{last_number + i}"

        bottle = Bottle(
            serial_number=serial,
            product=product,
            status="GODOWN"
        )
        bottles.append(bottle)

    Bottle.objects.bulk_create(bottles)

    for bottle in bottles:
        ledgers.append(
            BottleLedger(
                bottle=bottle,
                action="CREATE",
                reference=f"initial_stock_{date_str}"
            )
        )

    BottleLedger.objects.bulk_create(ledgers)

    return bottles


@csrf_exempt
def preview_bottles(request):
    data = json.loads(request.body)
    qty = int(data["qty"])
    prefix = data.get("prefix", "BTL")

    today = datetime.now().strftime("%d-%m")
    last_no = get_last_number(today, prefix)

    serials = [
        f"{today}-{prefix}{last_no + i}"
        for i in range(1, qty + 1)
    ]

    return JsonResponse({"serials": serials})


def bottle_generator_page(request):
    products = ProdutItemMaster.objects.exclude(
    category__category_name__icontains="coupon"
    )
    return render(request, "bottle_management/generate_bottle.html", {"products": products})


@csrf_exempt
def save_bottles(request):
    data = json.loads(request.body)

    product_id = data["product_id"]
    serials = data["serials"]

    product = ProdutItemMaster.objects.get(id=product_id)

    result = save_generated_bottles(
        product=product,
        serials=serials
    )

    return JsonResponse(result, status=201)

@transaction.atomic
def save_generated_bottles(*, product, serials, created_by=None):
    """
    Save generated bottle serial numbers into DB
    """

    if not serials:
        raise ValidationError("No serial numbers provided")

    # 1️⃣ Prevent duplicates
    existing = set(
        Bottle.objects.filter(
            serial_number__in=serials
        ).values_list("serial_number", flat=True)
    )

    if existing:
        raise ValidationError(
            f"Serials already exist: {', '.join(existing)}"
        )

    # 2️⃣ Bulk create bottles (NO FK usage yet)
    Bottle.objects.bulk_create([
        Bottle(
            serial_number=serial,
            product=product,
            status="GODOWN"
        )
        for serial in serials
    ])

    # 3️⃣ Re-fetch bottles WITH IDs
    created_bottles = Bottle.objects.filter(
        serial_number__in=serials
    )

    # 4️⃣ Create ledger entries
    BottleLedger.objects.bulk_create([
        BottleLedger(
            bottle=bottle,
            action="CREATE",
            reference="initial_stock",
          #   created_by=created_by
        )
        for bottle in created_bottles
    ])

    return {
        "created_count": len(created_bottles),
        "serials": serials
    }

@transaction.atomic
def map_nfc_to_bottle(*, bottle_id, nfc_uid, created_by=None):
    """
    Map NFC UID to a bottle (one-time operation)
    """

    nfc_uid = nfc_uid.strip()

    if not nfc_uid:
        raise ValidationError("NFC UID is required")

    
    if Bottle.objects.filter(nfc_uid=nfc_uid).exists():
        raise ValidationError("This NFC UID is already mapped to another bottle")

    
    bottle = Bottle.objects.select_for_update().get(id=bottle_id)

    
    if bottle.nfc_uid:
        raise ValidationError("This bottle already has NFC mapped")

    
    bottle.nfc_uid = nfc_uid
    bottle.save()

    
    BottleLedger.objects.create(
        bottle=bottle,
        action="MAP_NFC",
        reference=nfc_uid,
        created_by=created_by
    )

    return {
        "bottle": bottle.serial_number,
        "nfc_uid": nfc_uid,
        "status": "MAPPED"
    }


@csrf_exempt
def nfc_mapping_save(request):
    try:
        data = json.loads(request.body)

        bottle_id = data.get("bottle_id")
        nfc_uid = data.get("nfc_uid")

        result = map_nfc_to_bottle(
            bottle_id=bottle_id,
            nfc_uid=nfc_uid,
            created_by=request.user if request.user.is_authenticated else None
        )

        return JsonResponse(result, status=200)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def nfc_mapping_page(request):
    bottles = Bottle.objects.filter(nfc_uid__isnull=True)
    return render(
        request,
        "bottle_management/nfc_mapping.html",
        {"bottles": bottles}
    )