from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from trips.models import Trip, TripMember

from .filters import IdeaFilter
from .models import Idea
from .serializers import IdeaSerializer


class IdeaViewSet(viewsets.ModelViewSet):
    serializer_class = IdeaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IdeaFilter

    def get_trip(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        if not TripMember.objects.filter(trip=trip, user=self.request.user).exists():
            raise NotFound()
        return trip

    def get_queryset(self):
        trip = self.get_trip()
        return Idea.objects.filter(trip=trip).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(trip=self.get_trip(), author=self.request.user)