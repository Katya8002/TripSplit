from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from trips.models import Trip, TripMember

from .serializers import ScheduleItemSerializer


class ScheduleItemViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleItemSerializer
    permission_classes = [IsAuthenticated]

    def get_trip(self):
        if not hasattr(self, "_trip"):
            trips = Trip.objects.filter(members__user=self.request.user)
            self._trip = get_object_or_404(trips, pk=self.kwargs["trip_id"])
        return self._trip

    def check_permissions(self, request):
        super().check_permissions(request)
        trip = self.get_trip()
        is_organizer = TripMember.objects.filter(
            trip=trip, user=request.user, role=TripMember.Role.ORGANIZER
        ).exists()
        if request.method not in SAFE_METHODS and not is_organizer:
            raise PermissionDenied("Змінювати розклад може тільки організатор")

    def get_queryset(self):
        return self.get_trip().schedule_items.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["trip"] = self.get_trip()
        return context

    def perform_create(self, serializer):
        serializer.save(trip=self.get_trip())