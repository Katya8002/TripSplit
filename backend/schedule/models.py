from django.db import models


class ScheduleItem(models.Model):
    trip = models.ForeignKey(
        "trips.Trip", on_delete=models.CASCADE, related_name="schedule_items"
    )
    idea = models.ForeignKey(
        "ideas.Idea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="schedule_items",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["start"]
        indexes = [
            models.Index(fields=["trip", "start"], name="schedule_trip_start_idx"),
        ]

    def __str__(self):
        return f"{self.title} ({self.start:%Y-%m-%d %H:%M})"