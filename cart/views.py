from django.contrib.admin import action
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from .models import Cart, CartItem, Product, Order
from .serializers import CartSerializer, RemoveFromCartSerializer, CheckoutSerializer, AddToCartSerializer


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
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
    def create(self, request):
        cart = Cart.objects.filter(user=request.user, is_checked_out=False).first()
        if not cart:
            return Response({'detail': 'No cart found or cart is already checked out'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            cart=cart,
            total_price=cart.total_price(),
            status="Pending"
        )
        print(order)
        cart.is_checked_out = True
        cart.save()

        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)





