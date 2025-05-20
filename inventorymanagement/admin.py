from django.contrib import admin

from inventorymanagement.models import Category, Product, SubCategory

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
