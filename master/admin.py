from django.contrib import admin

from accounts.models import TermsAndConditions
from master.models import *

# Register your models here.
admin.site.register(CategoryMaster)
class BranchMasterAdmin(admin.ModelAdmin):
    list_display = ('branch_id', 'created_by', 'created_date', 'modified_by', 'modified_date', 'name', 'address', 'mobile', 'landline', 'phone', 'fax', 'trn', 'website', 'district', 'email', 'user_id', 'logo', 'is_exported')
admin.site.register(BranchMaster, BranchMasterAdmin)
admin.site.register(LocationMaster)
admin.site.register(LocationExportStatus)
class DistrictsAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','name']
admin.site.register(DistrictMaster,DistrictsAdmin)

class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','content']
admin.site.register(PrivacyPolicy,PrivacyPolicyAdmin)

class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['created_by','created_date','description']
admin.site.register(TermsAndConditions,TermsAndConditionsAdmin)

class SubscriptionSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_subscription_active', 'created_by', 'created_date')
admin.site.register(SubscriptionSettings, SubscriptionSettingsAdmin)