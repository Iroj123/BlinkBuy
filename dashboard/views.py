from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response

from authentication.serializers import UserSerializer

from cart.models import Order, CartItem, OrderItem
from inventorymanagement.models import Product
from inventorymanagement.serializers import OrderSerializer, ProductSerializer
from inventorymanagement.views import IsAdmin

User=get_user_model()

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class OrderListView(generics.ListAPIView):
    queryset = Order.objects.select_related('cart__user').prefetch_related('cart__items__product')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class AdminDashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        total_users = User.objects.filter(groups__name='User').count()
        total_vendors = User.objects.filter(groups__name='Vendor').count()
        total_products=Product.objects.all().count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
        total_products_ordered = OrderItem.objects.aggregate(total=Sum('quantity'))['total'] or 0

        return Response({
            'total_users': total_users,
            'total_vendors': total_vendors,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_products_ordered': total_products_ordered
        })

