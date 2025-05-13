from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'created_at','product']
        read_only_fields = ['user']