from django.urls import path
from .views import (
    CartDetailView,
    AddItemToCartView,
    UpdateCartItemView,
    RemoveItemFromCartView,
    ClearCartView
)

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/add_item/", AddItemToCartView.as_view(), name="add-item"),
    path("cart/update_item/<int:item_id>/", UpdateCartItemView.as_view(), name="update-item"),
    path("cart/remove_item/<int:item_id>/", RemoveItemFromCartView.as_view(), name="remove-item"),
    path("cart/clear/", ClearCartView.as_view(), name="clear-cart"),
]
