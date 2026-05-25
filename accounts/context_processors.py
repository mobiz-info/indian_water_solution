def user_tabs(request):
    tabs = []
    if request.user.is_authenticated and hasattr(request.user, "designation_id"):
        desig = request.user.designation_id
        if desig and desig.allowed_tabs:
            tabs = desig.allowed_tabs
    return {"user_tabs": tabs}