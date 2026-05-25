from django.shortcuts import redirect
from django.urls import reverse
from master.models import SubscriptionSettings

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # Allow static and media files
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)

        # Allow admin access so administrators can toggle the setting back
        if path.startswith('/admin/'):
            return self.get_response(request)

        # Allow the alert page itself to avoid infinite redirect loops
        try:
            alert_url = reverse('subscription_alert')
            if path == alert_url:
                return self.get_response(request)
        except Exception:
            pass

        # Check the subscription status
        try:
            settings = SubscriptionSettings.objects.first()
            if settings and settings.is_subscription_active:
                return redirect('subscription_alert')
        except Exception:
            # DB might not be migrated yet
            pass

        response = self.get_response(request)
        return response
