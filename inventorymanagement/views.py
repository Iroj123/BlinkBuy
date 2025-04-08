from django.db.models import Sum
from rest_framework import permissions, viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Order, CartItem
from inventorymanagement.models import Product
from inventorymanagement.serializers import ProductSerializer


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
    permission_classes = [IsVendor | IsAdmin]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    def get_queryset(self):
        if self.request.user.groups.filter(name='Admin').exists():
            return Product.objects.all()
        return Product.objects.filter(vendor=self.request.user)




class VendorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vendor = request.user

            # Get orders for this vendor
        orders = Order.objects.filter(vendor=vendor).select_related('user', 'cart')

        order_data = []

        print("Vendor:", vendor)
        print("Orders for vendor:", orders)

        for order in orders:
            items = order.cart.items.select_related('product')
            order_data.append({
                'order_id': order.id,
                'customer_email': order.user.email,
                'total_price': order.total_price,
                'status': order.status,
                'items': [
                        {
                            'product': item.product.name,
                            'quantity': item.quantity,
                            'price': item.product.price,
                        } for item in items if item.product.vendor == vendor
                    ]
                })

        return Response({'orders': order_data})

class VendorOrderView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]  # Ensure the user is authenticated and a vendor

    def get(self, request):
        vendor_user = request.user

        # Get all orders for this vendor
        orders = Order.objects.filter(vendor=vendor_user)

        order_details = []

        for order in orders:
            # For each order, get all cart items (products bought in the order)
            cart_items = CartItem.objects.filter(order=order)
            products = []

            for item in cart_items:
                product = item.product
                products.append({
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'price': item.price
                })

            # Assuming 'user' field in Order is the customer placing the order
            customer = order.user  # This assumes `order.user` is the customer (user) who placed the order

            order_details.append({
                'order_id': order.id,
                'user_name': f"{customer.first_name} {customer.last_name}",  # Display user's full name
                'order_total': order.total_price,
                'status': order.status,
                'products': products,
                'created_at': order.created_at
            })

        return Response({
            'orders': order_details
        })





