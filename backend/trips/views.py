from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Trip, TripMember
from .permissions import IsOrganizerOrReadOnly
from .serializers import JoinTripSerializer, TripMemberSerializer, TripSerializer


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

    @action(detail=False, methods=["post"])
    def join(self, request):
        serializer = JoinTripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trip = get_object_or_404(
            Trip, invite_code=serializer.validated_data["invite_code"]
        )
        _, created = TripMember.objects.get_or_create(trip=trip, user=request.user)
        data = TripSerializer(trip, context=self.get_serializer_context()).data
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(data, status=code)

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        trip = self.get_object()
        members = trip.members.select_related("user")
        return Response(TripMemberSerializer(members, many=True).data)

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"members/(?P<user_id>\d+)",
        permission_classes=[IsAuthenticated],
    )
    def remove_member(self, request, pk=None, user_id=None):
        trip = self.get_object()
        is_organizer = trip.members.filter(
            user=request.user, role=TripMember.Role.ORGANIZER
        ).exists()
        if not is_organizer and request.user.id != int(user_id):
            raise PermissionDenied("Прибрати учасника може тільки організатор")
        member = get_object_or_404(trip.members.all(), user_id=user_id)
        if member.role == TripMember.Role.ORGANIZER:
            return Response(
                {"detail": "Організатора не можна прибрати з поїздки"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)