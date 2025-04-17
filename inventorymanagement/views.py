from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, generics, filters, status
from rest_framework.generics import  ListCreateAPIView
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


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.groups.filter(name='Admin').exists()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser,FormParser, JSONParser]
    permission_classes = [IsVendor | IsAdmin]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    def get_queryset(self):
        if self.request.user.groups.filter(name='Admin').exists():
            return Product.objects.all()
        return Product.objects.filter(vendor=self.request.user)


class CategoryCreateView(ListCreateAPIView):
    queryset = Category.objects.all()  # Define queryset
    serializer_class = CategorySerializer  # Define the serializer
    permission_classes = [IsAdmin]  #





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

        order_details = []

        for order in orders:
            # For each order, get all cart items (products bought in the order)
            cart_items = order.cart.items.all()
            products = []

            for item in cart_items:
                product = item.product
                products.append({
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'price': item.total_price()
                })

            # Assuming 'user' field in Order is the customer placing the order
            customer = order.user  # This assumes `order.user` is the customer (user) who placed the order

            order_details.append({
                'order_id': order.id,
                'user_name': f"{customer.firstname} {customer.lastname}",  # Display user's full name
                'order_total': order.total_price,
                'status': order.status,
                'products': products,

            })
        return Response({
            'orders': order_details
        })

    def patch(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order belonging to this vendor
        order = get_object_or_404(Order, id=order_id, vendor=request.user)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Order status updated successfully.', 'order': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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