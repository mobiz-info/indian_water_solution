import os
import sys
sys.path.append('/Users/muhammedanshid/Desktop/mobiz_projects/sana_water_backend')
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sales_management.models import CollectionPayment, Receipt

print("=== CollectionPayments with Cheque ===")
for cp in CollectionPayment.objects.filter(payment_method__iexact="cheque")[:10]:
    print(f"ID: {cp.id}, Customer: {cp.customer}, Amount: {cp.amount_received}, Receipt Num: {cp.receipt_number}")

print("\n=== CollectionCheque status for 67048 ===")
from sales_management.models import CollectionCheque
for cc in CollectionCheque.objects.filter(collection_payment_id=67048):
    print(f"CollectionPayment ID: {cc.collection_payment_id}, Cheque No: {cc.cheque_no}, Status: {cc.status}")



