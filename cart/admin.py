from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "total_price_display")
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at",)

    def total_price_display(self, obj):
        return f"${obj.total_price():.2f}"
    total_price_display.short_description = "Total Price"

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product_name", "product_price", "quantity", "total_price_display", "product_image_display")
    search_fields = ("product__name",)
    list_filter = ("cart",)

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Product Name"

    def product_price(self, obj):
        return f"${obj.product.price:.2f}"
    product_price.short_description = "Product Price"

    def total_price_display(self, obj):
        return f"${obj.total_price():.2f}"
    total_price_display.short_description = "Total Price"

    def product_image_display(self, obj):
        if obj.product.image:
            return f'<img src="{obj.product.image.url}" width="50" height="50" style="border-radius: 5px;" />'
        return "No Image"
    product_image_display.short_description = "Image"
    product_image_display.allow_tags = True  # ✅ Allow HTML rendering in admin panel
