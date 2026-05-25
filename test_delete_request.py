import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sana_water_backend.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from client_management.models import CustomerCoupon

c = Client()
# Log in first or we might get 302 redirect to login.
# The view has @login_required? Let's check.
from accounts.models import CustomUser
user = CustomUser.objects.filter(is_superuser=True).first()
if user:
    c.force_login(user)

coupon_recharge = CustomerCoupon.objects.last()
if coupon_recharge:
    url = reverse('delete_coupon_recharge', args=[coupon_recharge.pk])
    print(f"Requesting URL: {url}")
    response = c.get(url)
    print(f"Status: {response.status_code}")
    print(f"Redirect URL: {response.url if hasattr(response, 'url') else 'None'}")
    
    # Check messages
    from django.contrib.messages import get_messages
    messages = list(get_messages(response.wsgi_request))
    for m in messages:
        print(f"Message: {m}")
        
