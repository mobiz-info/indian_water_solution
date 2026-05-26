def user_tabs(request):
    tabs = []
    if request.user.is_authenticated:
        if request.user.is_superuser:
            tabs = [
                "dashboard", "master", "accounts", "sales", "daily_sales", 
                "reports", "van", "products", "clients", "clients.outstanding_crud", 
                "clients.price_change", "clients.collection", "coupon", "customercare", 
                "bottle", "audit", "invoice", "receipt", "settings"
            ]
        elif hasattr(request.user, "designation_id"):
            desig = request.user.designation_id
            if desig and desig.allowed_tabs:
                tabs = desig.allowed_tabs
    return {"user_tabs": tabs}