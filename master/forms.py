from django import forms
from django.forms import ModelForm
from .models import *
from accounts.models import TermsAndConditions
from ckeditor.widgets import CKEditorWidget

class Branch_Create_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['district'].queryset = DistrictMaster.objects.filter()
    class Meta:
        model = BranchMaster
        fields = ['name', 'address', 'mobile', 'phone', 'fax','website','email','logo','district','landline','trn']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'fax':forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'website': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'true'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-control', 'required': 'true'}),
            'landline': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'trn': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Branch_Edit_Form(forms.ModelForm):
    district = forms.ModelChoiceField(
        queryset=DistrictMaster.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'true'})
    )
    class Meta:
        model = BranchMaster
        fields = ['name', 'address', 'mobile', 'phone', 'fax','website','email','logo','district','landline','trn']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'fax':forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'website': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'true'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'landline': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'trn': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Route_Create_Form(forms.ModelForm):
    class Meta:
        model = RouteMaster
        fields = ['route_name','branch_id']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Route_Edit_Form(forms.ModelForm):

    class Meta:
        model = RouteMaster
        fields = ['route_name']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Designation_Create_Form(forms.ModelForm):
    TAB_CHOICES = [
        ("dashboard", "Dashboard"),
        ("master", "Master"),
        ("accounts", "Accounts"),
        ("sales", "Sales Management"),
        ("daily_sales", "Daily Sales Reports"),
        ("reports", "Reports"),
        ("van", "Van Management"),
        ("products", "Product Management"),
        ("clients", "Client Management"),
        ("clients.outstanding_crud", "\u2003\u2514 Outstanding – Create / Edit / Delete"),
        ("clients.price_change", "\u2003\u2514 Customer Price Change"),
        ("clients.collection", "\u2003\u2514 Collection in Customer List"),
        ("coupon", "Coupon Management"),
        ("customercare", "Customer Care"),
        ("bottle", "Bottle Management"),
        ("audit", "Audit Management"),
        ("invoice", "Invoice Management"),
        ("receipt", "Receipt"),
        ("settings", "Settings"),
    ]
    allowed_tabs = forms.MultipleChoiceField(
        choices=TAB_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = DesignationMaster
        fields = ['designation_name','allowed_tabs']
        widgets = {
            'designation_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Designation_Edit_Form(forms.ModelForm):
    TAB_CHOICES = [
        ("dashboard", "Dashboard"),
        ("master", "Master"),
        ("accounts", "Accounts"),
        ("sales", "Sales Management"),
        ("daily_sales", "Daily Sales Reports"),
        ("reports", "Reports"),
        ("van", "Van Management"),
        ("products", "Product Management"),
        ("clients", "Client Management"),
        ("clients.outstanding_crud", "\u2003\u2514 Outstanding – Create / Edit / Delete"),
        ("clients.price_change", "\u2003\u2514 Customer Price Change"),
        ("clients.collection", "\u2003\u2514 Collection in Customer List"),
        ("coupon", "Coupon Management"),
        ("customercare", "Customer Care"),
        ("bottle", "Bottle Management"),
        ("audit", "Audit Management"),
        ("invoice", "Invoice Management"),
        ("receipt", "Receipt"),
        ("settings", "Settings"),
    ]
    allowed_tabs = forms.MultipleChoiceField(
        choices=TAB_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = DesignationMaster
        fields = ['designation_name','allowed_tabs']
        widgets = {
            'designation_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Location_Add_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = LocationMaster
        fields = ['location_name', 'district']
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'district': forms.Select(attrs={'class': 'form-control', 'required': True})
        }


class Location_Edit_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['area'].queryset = Area.objects.filter(is_dlt=False)
    class Meta:
        model = LocationMaster
        fields = ['location_name', 'district']
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'district': forms.Select(attrs={'class': 'form-control', 'required': True})
        }
    
    class Location_Add_Form(forms.ModelForm):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    class Meta:
        model = LocationMaster
        fields = ['location_name', 'district']
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'district': forms.Select(attrs={'class': 'form-control', 'required': True})
        }


class Location_Edit_Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['area'].queryset = Area.objects.filter(is_dlt=False)
    class Meta:
        model = LocationMaster
        fields = ['location_name', 'district']
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'district': forms.Select(attrs={'class': 'form-control', 'required': True})
        }

class Category_Create_Form(forms.ModelForm):
    class Meta:
        model = CategoryMaster
        fields = ['category_name']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

class Category_Edit_Form(forms.ModelForm):

    class Meta:
        model = CategoryMaster
        fields = ['category_name']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }
        
        
class TermsAndConditionsForm(forms.ModelForm):
    class Meta:
        model = TermsAndConditions
        fields = ['description']
        widgets = {
            'description': CKEditorWidget(),
        }

class PrivacyForm(forms.ModelForm):
    class Meta:
        model = PrivacyPolicy
        fields = ['content']
        widgets = {
            'content': CKEditorWidget(),
        }
class PermissionManagementTabForm(forms.ModelForm):
    class Meta:
        model = PermissionManagementTab
        fields = ['tab_name', 'department']

        widgets = {
            'tab_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Tab Name'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

class District_Form(forms.ModelForm):
    class Meta:
        model = DistrictMaster
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}),
        }