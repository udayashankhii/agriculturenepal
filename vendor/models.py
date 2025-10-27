from django.db import models
from django.conf import settings

# Create your models here.
from django.contrib.auth.models import User

class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    pan_number_image = models.ImageField(upload_to='pan_numbers/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(default='No description provided')  # Added default value
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name