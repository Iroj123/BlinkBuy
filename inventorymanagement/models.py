from django.contrib.auth import get_user_model
from django.db import models


User=get_user_model()

class Product(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(decimal_places=2,max_digits=10)
    stock=models.IntegerField()
    vendor=models.ForeignKey(User,on_delete=models.CASCADE,related_name='products')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)




    def __str__(self):
        return self.name



