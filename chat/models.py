from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import ForeignKey

User=get_user_model()
# Create your models here.

class Chat(models.Model):
    user=ForeignKey(User,on_delete=models.CASCADE,related_name='user_chats')
    vendor=ForeignKey(User,on_delete=models.CASCADE,related_name='vendor_chats')
    created_at=models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat=ForeignKey(Chat,on_delete=models.CASCADE,related_name='messages')
    sender=ForeignKey(User,on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages',null=True)

    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)