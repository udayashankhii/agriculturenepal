from rest_framework import serializers
from .models import Customer, Order, OrderItem

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'city', 'phone']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'total_amount', 'payment_method', 'payment_status', 'shop_name', 'created_at']

    def create(self, validated_data):
        customer_data = validated_data.pop('customer')
        items_data = validated_data.pop('items')

        customer, _ = Customer.objects.get_or_create(phone=customer_data['phone'], defaults=customer_data)
        order = Order.objects.create(customer=customer, **validated_data)

        for item in items_data:
            OrderItem.objects.create(order=order, **item)

        return order
