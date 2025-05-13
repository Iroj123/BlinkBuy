from django.contrib.auth import get_user_model
from django.db import models


User=get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(decimal_places=2,max_digits=10)
    stock=models.IntegerField()
    vendor=models.ForeignKey(User,on_delete=models.CASCADE,related_name='products')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    thumbnail=models.ImageField(upload_to='products/thumbnails/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)


    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock > 0

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([review.rating for review in reviews]) / reviews.count(), 1)
        return 0.0



class ProductImages(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to='product_images/')





