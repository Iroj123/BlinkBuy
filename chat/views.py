from django.shortcuts import render
from rest_framework.generics import GenericAPIView

# views.py
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Chat
from django.contrib.auth import get_user_model

from .serializers import CreateChatSerializer

User = get_user_model()

class CreateChatView(APIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = CreateChatSerializer



    def post(self, request):
        vendor_id = request.data.get("vendor_id")
        print("Request user:", request.user)

        print("Received vendor_id:", vendor_id)

        try:
            vendor = User.objects.get(id=vendor_id)
        except User.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=404)

