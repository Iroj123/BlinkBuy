from rest_framework import serializers

from cart.models import Order
from inventorymanagement.models import Product, ProductImages, Category, SubCategory
from reviews.serializers import ReviewSerializer


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = ProductImages
        fields = ['id', 'image']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['name', 'images', 'description','subcategory', 'stock', 'price', 'created_at', 'updated_at', "thumbnail",'in_stock','average_rating','reviews']

    def get_in_stock(self, obj):
        return obj.stock > 0

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])  # extract image list
        product = Product.objects.create(**validated_data)  # create product
        for image in images_data:
            ProductImages.objects.create(product=product, image=image)  # save each image
        return product

    def get_fields(self):
        fields = super().get_fields()
        # Ensure 'view' is in context and has 'action'
        view = self.context.get('view', None)
        if view and hasattr(view, 'action') and view.action.lower() == "create":
            # Add 'images' field dynamically during create
            fields['images'] = serializers.ListField(
                child=serializers.FileField(),
                write_only=True
            )

        return fields

    def to_representation(self, instance):
        representation = super(ProductSerializer, self).to_representation(instance)
        representation['images'] = ImageSerializer(instance.images.all(), context=self.context, many=True).data
        return representation

    def get_average_rating(self, obj):
        return obj.average_rating()




class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_date', 'total_price', 'status']




class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name','subcategories']
