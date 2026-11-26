from django.conf import settings
from django.db import models

from ideas.models import Idea
from trips.models import Trip


class Poll(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="polls")
    title = models.CharField(max_length=200)
    deadline = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    winner = models.ForeignKey(
        Idea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_polls",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_polls",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="poll_options")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "idea"], name="unique_poll_option"),
        ]


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="poll_votes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "user"], name="unique_poll_vote"),
        ]
