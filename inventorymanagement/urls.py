from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventorymanagement.views import ProductViewSet,  VendorOrderView, VendorDashboardView
router=DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [path('', include(router.urls)),
               path('vendor-dashboard/', VendorDashboardView.as_view()),
               path('order/',VendorOrderView.as_view()),
               ]