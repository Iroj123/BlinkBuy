
from rest_framework import serializers

from cart.models import CartItem, Cart, Order, OrderItem
from inventorymanagement.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = ['id','product', 'quantity','total_price']

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id','items', 'total_price','is_checked_out']

    def get_total_price(self, obj):
        return obj.total_price()


class RemoveFromCartSerializer(serializers.Serializer):
    cart_item_id = serializers.IntegerField()

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class CheckoutSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)  # use related_name='items'

    class Meta:
        model = Order
        fields = ['id', 'order_date', 'vendor', 'total_price', 'status', 'items']



