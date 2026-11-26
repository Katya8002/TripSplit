from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from trips.models import Trip, TripMember

from .models import Poll, PollOption, Vote
from .serializers import (
    CloseInputSerializer,
    PollSerializer,
    VoteInputSerializer,
)


class PollViewSet(viewsets.ModelViewSet):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_trip(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_id"])
        if not TripMember.objects.filter(trip=trip, user=self.request.user).exists():
            raise NotFound()
        return trip

    def is_organizer(self, trip):
        return TripMember.objects.filter(
            trip=trip, user=self.request.user, role=TripMember.Role.ORGANIZER
        ).exists()

    def get_queryset(self):
        trip = self.get_trip()
        return Poll.objects.filter(trip=trip).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["trip"] = self.get_trip()
        return context

    def perform_create(self, serializer):
        trip = self.get_trip()
        if not self.is_organizer(trip):
            raise PermissionDenied()
        serializer.save(trip=trip, created_by=self.request.user)

    def finalize(self, poll, winner_option):
        poll.status = Poll.Status.CLOSED
        poll.winner = winner_option.idea
        poll.save()
        winner_option.idea.status = winner_option.idea.Status.APPROVED
        winner_option.idea.save()
        for option in poll.options.exclude(pk=winner_option.pk):
            option.idea.status = option.idea.Status.REJECTED
            option.idea.save()

    @action(detail=True, methods=["post"])
    def vote(self, request, trip_id=None, pk=None):
        poll = self.get_object()
        if poll.status != Poll.Status.OPEN or poll.deadline <= timezone.now():
            return Response(
                {"detail": "Голосування завершене"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = VoteInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        option = get_object_or_404(
            PollOption, pk=serializer.validated_data["option"], poll=poll
        )
        if Vote.objects.filter(poll=poll, user=request.user).exists():
            return Response(
                {"detail": "Ви вже проголосували"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Vote.objects.create(poll=poll, option=option, user=request.user)
        return Response(self.get_serializer(poll).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def close(self, request, trip_id=None, pk=None):
        poll = self.get_object()
        if not self.is_organizer(poll.trip):
            raise PermissionDenied()
        if poll.status == Poll.Status.CLOSED:
            return Response(
                {"detail": "Голосування вже закрите"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        input_serializer = CloseInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        ranked = list(
            poll.options.annotate(total=Count("votes")).order_by("-total")
        )
        top = [option for option in ranked if option.total == ranked[0].total]
        if len(top) > 1:
            chosen_id = input_serializer.validated_data.get("winner_option")
            chosen = next((o for o in top if o.pk == chosen_id), None)
            if chosen is None:
                return Response(
                    {
                        "detail": "Нічия: оберіть переможця",
                        "tied_options": [option.pk for option in top],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            winner = chosen
        else:
            winner = top[0]
        self.finalize(poll, winner)
        return Response(self.get_serializer(poll).data)