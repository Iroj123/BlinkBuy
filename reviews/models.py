from django.db import models

class Review(models.Model):
    product=models.ForeignKey('inventorymanagement.Product',on_delete=models.CASCADE,related_name='reviews')
    user=models.ForeignKey('authentication.CustomUser',on_delete=models.CASCADE,related_name='reviews')
    rating=models.PositiveSmallIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Prevent multiple reviews from same user

    def __str__(self):
        return f"{self.user} rated {self.product} {self.rating} stars"