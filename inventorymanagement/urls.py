from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventorymanagement.views import ProductViewSet, VendorOrderView, VendorDashboardView, ProductSearchView, \
    OrderSearchView, UserSearchView, CategoryCreateView

router=DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
# router.register('product-images', ProductImageUploadViewSet, basename='product-image')


urlpatterns = [path('', include(router.urls)),
               path('vendor-dashboard/', VendorDashboardView.as_view()),
               path('order/',VendorOrderView.as_view()),
                path('order/<int:pk>/', VendorOrderView.as_view()),

               path('search/products/', ProductSearchView.as_view(), name='search-products'),
               path('search/orders/', OrderSearchView.as_view(), name='search-orders'),
               path('search/users/', UserSearchView.as_view(), name='search-users'),
               path('category/create/', CategoryCreateView.as_view(), name='create-category'),

               ]