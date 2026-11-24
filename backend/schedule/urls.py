from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ScheduleItemViewSet

router = SimpleRouter()
router.register("schedule", ScheduleItemViewSet, basename="schedule")

urlpatterns = [
    path("trips/<int:trip_id>/", include(router.urls)),
]