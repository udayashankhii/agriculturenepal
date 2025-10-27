from django.contrib import admin
from .models import Vendor, Product

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'user', 'phone_number', 'is_active', 'registration_date']
    search_fields = ['shop_name', 'user__username']
    list_filter = ['is_active', 'registration_date']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'price', 'stock', 'category', 'created_at']
    search_fields = ['name', 'vendor__shop_name']
    list_filter = ['category', 'created_at']
