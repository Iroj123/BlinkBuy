from rest_framework import serializers

from cart.models import Order
from inventorymanagement.models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    from cart.serializers import CartSerializer

    cart = CartSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'cart', 'order_date', 'total_price', 'status']
