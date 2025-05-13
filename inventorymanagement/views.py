from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, generics, filters, status
from rest_framework.generics import  ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.serializers import UserSerializer
from cart.models import Order, CartItem
from inventorymanagement.models import Product, Category
from inventorymanagement.serializers import ProductSerializer, OrderSerializer, CategorySerializer


class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Vendor').exists()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                not request.user.groups.filter(name__in=['Admin', 'Vendor']).exists()
        )
class IsAdminOrIsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                request.user.groups.filter(name__in=['Admin', 'Vendor']).exists()
        )
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.groups.filter(name='Admin').exists()

class PageNumberPagination(PageNumberPagination):
    page_size=10
    page_size_query_param = 'page_size'
    max_page_size = 100
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser,FormParser, JSONParser]
    # permission_classes = [IsVendor | IsAdmin]
    pagination_class = PageNumberPagination

    def get_permissions(self):
        # Allow anyone to read (GET, HEAD, OPTIONS)
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        # Only vendors or admins can write
        return [IsAdminOrIsVendor()]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    def get_queryset(self):
        user = self.request.user

        # If the user is unauthenticated (AnonymousUser), show all products
        if not user.is_authenticated:
            return Product.objects.all()

        # If the user is in Admin group, show all products
        if user.groups.filter(name='Admin').exists():
            return Product.objects.all()

        # If the user is a vendor, show only their products
        if user.groups.filter(name='Vendor').exists():
            return Product.objects.filter(vendor=user)

        # If the user is authenticated but not a vendor or admin (just a regular user)
        return Product.objects.all()

class CategoryCreateView(ListCreateAPIView):
    queryset = Category.objects.all()  # Define queryset
    serializer_class = CategorySerializer  # Define the serializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrIsVendor()]
        return [AllowAny()]




class VendorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vendor = request.user
        orders = Order.objects.filter(vendor=vendor).select_related('user', 'cart')

        total_quantity = 0
        total_revenue = 0
        product_ids = set()  # to track distinct products sold
        total_orders = orders.count()  # Count the total number of orders


        for order in orders:
            items = order.cart.items.select_related('product')
            for item in items:
                if item.product.vendor == vendor:
                    total_quantity += item.quantity
                    total_revenue += item.product.price * item.quantity
                    product_ids.add(item.product.id)

        return Response({
            'total_orders': total_orders,  # Total number of orders

            'products_sold_count': len(product_ids),        # distinct products sold
            'total_items_sold': total_quantity,             # total quantity
            'total_revenue': total_revenue                  # sum of price × quantity
        })


class VendorOrderView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]  # Ensure the user is authenticated and a vendor
    serializer_class = OrderSerializer
    def get(self, request):
        vendor_user = request.user

        # Get all orders for this vendor
        orders = Order.objects.filter(vendor=vendor_user)

        if not orders.exists():
            return Response({'message': 'No orders found'}, status=status.HTTP_404_NOT_FOUND)

        order_details = []

        for order in orders:
            order_items = order.items.select_related('product')  # OrderItem relation

            products = [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': item.get_total_price()
                }
                for item in order_items
            ]

            customer = order.user  # Customer who placed the order

            order_details.append({
                'order_id': order.id,
                'user_name': f"{customer.firstname} {customer.lastname}",
                'order_total': order.total_price,
                'status': order.status,
                'products': products,
                'order_date': order.order_date
            })

        return Response({'orders': order_details}, status=200)

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order belonging to this vendor
        order = get_object_or_404(Order, id=order_id, vendor=request.user)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Order status updated successfully.', 'order': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')  # Get the 'order_id' from the URL parameter
        if not order_id:
            return Response({'error': 'order_id is required in the URL'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the order belongs to this vendor
        order = get_object_or_404(Order, id=order_id, vendor=request.user)

        order.delete()  # Delete the order

        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name','category']


class OrderSearchView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['order_date', 'total_price', 'status']

class UserSearchView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'phoneno']