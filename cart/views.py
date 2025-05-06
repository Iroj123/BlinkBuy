from collections import defaultdict

from django.contrib.admin import action
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from .models import Cart, CartItem, Product, Order, OrderItem
from .serializers import CartSerializer, RemoveFromCartSerializer, CheckoutSerializer, AddToCartSerializer


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        pass

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)




class AddToCartViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddToCartSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            {'detail': 'Product added to cart'},
            status=status.HTTP_201_CREATED
        )




class RemoveFromCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RemoveFromCartSerializer

    def get_queryset(self):
        pass

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            cart_item_id = serializer.validated_data['cart_item_id']
            cart_item = CartItem.objects.filter(id=cart_item_id, cart__user=request.user).first()
            if not cart_item:
                return Response({'detail': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

            cart_item.delete()
            return Response({'detail': 'Product removed from cart'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CheckoutSerializer
    queryset = Order.objects.all()

    @transaction.atomic

    def create(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({'detail': 'No cart found or cart is already checked out'}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            # Group items by vendor
        vendor_items = defaultdict(list)
        for item in cart.items.select_related('product'):

            if item.product.stock < item.quantity:
                return Response({
                    'detail': f"'{item.product.name}' has only {item.product.stock} in stock."
                }, status=status.HTTP_400_BAD_REQUEST)

            vendor = item.product.vendor
            vendor_items[vendor].append(item)
        created_orders = []
        for vendor, items in vendor_items.items():
            order = Order.objects.create(
                cart=cart,
                vendor=vendor,
                user=request.user,
                total_price=sum([item.product.price * item.quantity for item in items]),
                status='Pending'
            )

            for item in items:
                product = item.product
                product.stock -= item.quantity
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price  # store current price
            )

            created_orders.append(order)

        cart.save()
        cart.items.all().delete()  # ✅ Clear the items if using FK

        serializer = self.get_serializer(created_orders, many=True)
        return Response({
            'message': 'Order(s) placed successfully.',
            'orders': serializer.data
        }, status=status.HTTP_201_CREATED)




