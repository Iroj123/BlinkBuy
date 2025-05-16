from django.urls import path

from chat.views import CreateChatView

urlpatterns = [
    path('chat',CreateChatView.as_view()),
]