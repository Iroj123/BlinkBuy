import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlinkBuy.settings')
django.setup()

from chat.models import Chat, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = self.scope["user"]

        recipient = await self.get_recipient(self.chat_id, sender)
        if not recipient:
            await self.send(text_data=json.dumps({"error": "Unauthorized"}))
            return

        await self.save_message(self.chat_id, sender, recipient, message)

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender.id,
                "recipient_id": recipient.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "recipient_id": event["recipient_id"],
        }))

    @sync_to_async
    def save_message(self, chat_id, sender, recipient, message):
        chat = Chat.objects.get(id=chat_id)
        return Message.objects.create(chat=chat, sender=sender, recipient=recipient,content=message)

    @sync_to_async
    def is_participant(self, chat_id, user):
        try:
            chat = Chat.objects.get(id=chat_id)
            return chat.user == user or chat.vendor == user
        except Chat.DoesNotExist:
            return False

    @sync_to_async
    def get_recipient(self, chat_id, sender):
        try:
            chat = Chat.objects.get(id=chat_id)
            if chat.user == sender:
                return chat.vendor
            elif chat.vendor == sender:
                return chat.user
            return None
        except Chat.DoesNotExist:
            return None
