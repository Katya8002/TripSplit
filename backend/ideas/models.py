from django.conf import settings
from django.db import models

from trips.models import Trip


class Idea(models.Model):
    class Category(models.TextChoices):
        FOOD = "food", "Food"
        ATTRACTION = "attraction", "Attraction"
        NATURE = "nature", "Nature"
        ACCOMMODATION = "accommodation", "Accommodation"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="ideas")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ideas",
    )
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    link = models.URLField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
