from rest_framework import serializers
from .models import Cart, CartItem
from vendor.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

# ✅ 1️⃣ Product Serializer (Includes Image)
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "price", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

# ✅ 2️⃣ Cart Item Serializer
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price()

# ✅ 3️⃣ Cart Serializer (Includes User Details)
class CartSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price"]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email
        }

    def get_total_price(self, obj):
        return obj.total_price()
