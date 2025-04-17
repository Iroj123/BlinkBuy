from django.contrib.auth import get_user_model
from django.db import models
from inventorymanagement.models import Product


class Comment(models.Model):
    content=models.TextField()
    product=models.ForeignKey('inventorymanagement.Product',on_delete=models.CASCADE,related_name='comments')
    user=models.ForeignKey('authentication.CustomUser',on_delete=models.CASCADE,related_name='comments')
    created_at=models.DateTimeField(auto_now_add=True)

    def __Str__(self):
        return f"{self.user.email} on {self.product.name}"

