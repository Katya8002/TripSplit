import uuid

from django.conf import settings
from django.db import models


class Trip(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    invite_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TripMember(models.Model):
    class Role(models.TextChoices):
        ORGANIZER = "organizer", "Organizer"
        PARTICIPANT = "participant", "Participant"

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trip_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARTICIPANT)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["trip", "user"], name="unique_trip_member"),
        ]

    def __str__(self):
        return f"{self.user} in {self.trip} ({self.role})"