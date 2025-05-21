from rest_framework import serializers

from comment.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    email=serializers.SerializerMethodField()
    class Meta:
        model=Comment
        fields=['id','user','email','product','content','created_at','parent','replies']
        read_only_fields = ['id', 'user', 'created_at']
    def get_replies(self, obj):
        depth = self.context.get('depth', 1)
        if depth > 0 and obj.replies.exists():
            serializer = CommentSerializer(
                obj.replies.all(),
                many=True,
                context={'depth': depth - 1}
            )
            return serializer.data
        return []
    def get_email(self,obj):
        return obj.user.email