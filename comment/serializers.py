from rest_framework import serializers

from comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=['id','user','product','content','created_at']
        read_only_fields = ['id', 'user', 'created_at']
