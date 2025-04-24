from django.db import models


class Comment(models.Model):
    content=models.TextField()
    product=models.ForeignKey('inventorymanagement.Product',on_delete=models.CASCADE,related_name='comments')
    user=models.ForeignKey('authentication.CustomUser',on_delete=models.CASCADE,related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    def __Str__(self):
        return f"{self.user.email} on {self.product.name}"

    @property
    def is_reply(self):
        return self.parent is not None

