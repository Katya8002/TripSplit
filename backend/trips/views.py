from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Trip, TripMember
from .permissions import IsOrganizerOrReadOnly
from .serializers import TripSerializer


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]

    def get_queryset(self):
        return Trip.objects.filter(members__user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        trip = serializer.save()
        TripMember.objects.create(
            trip=trip, user=self.request.user, role=TripMember.Role.ORGANIZER
        )