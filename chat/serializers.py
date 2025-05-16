from chat.models import Chat
from rest_framework.serializers import ModelSerializer

class CreateChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = ['vendor']
