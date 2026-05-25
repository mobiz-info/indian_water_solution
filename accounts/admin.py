from django.contrib import admin
from .models import *

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id','first_name', 'last_name','username')
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = ("user_type",)
    ordering = ('-id',)
admin.site.register(CustomUser,CustomUserAdmin)

class CustomersAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_name', 'created_date', 'custom_id','visit_schedule')
    ordering = ('-created_date',)
    search_fields = ('customer_name', 'custom_id') 
admin.site.register(Customers,CustomersAdmin)

class SendNotificationAdmin(admin.ModelAdmin):
    list_display = ('device_token', 'user', 'created_on')
    ordering = ('-created_on',)
admin.site.register(Send_Notification,SendNotificationAdmin)
admin.site.register(GpsLog)
admin.site.register(CustomUserExportStatus)

@admin.register(Processing_Log)
class ProcessingLogAdmin(admin.ModelAdmin):
    # This shows these columns in the list view
    list_display = ('created_by', 'created_date', 'description')
    
    # This adds a filter sidebar for dates
    list_filter = ('created_date', 'created_by')
    search_fields = ('description', 'created_by')
    
    # This makes 'created_date' visible in the detail view 
    # (since auto_now_add fields are hidden by default)
    readonly_fields = ('created_date',)
