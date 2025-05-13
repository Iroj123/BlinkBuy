from django.urls import path

from comment.views import CreateCommentView, ProductCommentView, VendorCommentView

urlpatterns = [
    path('comments/', CreateCommentView.as_view(), name='create-comment'),
    path('products/<int:product_id>/comments/', ProductCommentView.as_view(), name='product-comments'),
    path('vendor/comments/', VendorCommentView.as_view(), name='vendor-comments'),

]