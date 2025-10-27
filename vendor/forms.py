from django import forms
from .models import Vendor, Product

class VendorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['shop_name', 'phone_number', 'address', 'pan_number_image']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image']