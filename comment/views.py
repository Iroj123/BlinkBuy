from rest_framework import generics, permissions

from comment.models import Comment
from comment.serializers import CommentSerializer
from inventorymanagement.views import IsVendor


class CreateCommentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductCommentView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product = self.kwargs['product_id']
        return Comment.objects.filter(product__id=product).order_by('-created_at')

class VendorCommentView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,IsVendor]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(product__vendor=self.request.user).order_by('-created_at')




