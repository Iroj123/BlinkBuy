from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)