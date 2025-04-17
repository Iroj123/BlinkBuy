from django.contrib.auth import get_user_model
from django.db import models

from inventorymanagement.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_checked_out = models.BooleanField(default=False)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.email}"


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )

    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES,max_length=50, default="Pending")
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_orders',blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders',blank=True, null=True)

    def __str__(self):
        return f"Order for {self.cart.user}"

