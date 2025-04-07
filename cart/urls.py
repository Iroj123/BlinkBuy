# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import CartViewSet, CheckoutViewSet, AddToCartViewSet, RemoveFromCartViewSet

router = DefaultRouter()
router.register(r'add', AddToCartViewSet, basename='add-to-cart')
router.register(r'remove', RemoveFromCartViewSet, basename='remove-from-cart')
router.register(r'checkout', CheckoutViewSet, basename='checkout')
router.register(r'', CartViewSet, basename='cart')
urlpatterns = [
    path('', include(router.urls)),
]
