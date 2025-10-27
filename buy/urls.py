from django.urls import path
from .views import create_order, list_orders

urlpatterns = [
    path('orders/create/', create_order, name='create_order'),
    path('orders/', list_orders, name='list_orders'),
]
