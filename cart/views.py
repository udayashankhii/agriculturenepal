from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Cart, CartItem
from vendor.models import Product
from .serializers import CartSerializer, CartItemSerializer

# ✅ 1️⃣ Get Cart Details
class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data)

# ✅ 2️⃣ Add Item to Cart
class AddItemToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": "Product added to cart"}, status=status.HTTP_201_CREATED)

# ✅ 3️⃣ Update Cart Item Quantity
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        quantity = request.data.get("quantity")
        if quantity is None or int(quantity) < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.quantity = int(quantity)
            cart_item.save()
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Quantity updated"}, status=status.HTTP_200_OK)

# ✅ 4️⃣ Remove Item from Cart
class RemoveItemFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

# ✅ 5️⃣ Clear Entire Cart
class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
            return Response({"message": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "No cart found"}, status=status.HTTP_404_NOT_FOUND)
