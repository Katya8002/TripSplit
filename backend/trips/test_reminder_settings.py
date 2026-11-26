import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from trips.models import Trip, TripMember

User = get_user_model()


def make_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def anna(db):
    return User.objects.create_user(username="anna", password="StrongPass123")


@pytest.fixture
def ivan(db):
    return User.objects.create_user(username="ivan", password="StrongPass123")


@pytest.fixture
def trip(anna, ivan):
    trip = Trip.objects.create(
        title="Lviv", start_date="2026-12-01", end_date="2026-12-03"
    )
    TripMember.objects.create(trip=trip, user=anna, role=TripMember.Role.ORGANIZER)
    TripMember.objects.create(trip=trip, user=ivan)
    return trip


def test_reminders_disabled_by_default(anna, trip):
    response = make_client(anna).get(f"/api/trips/{trip.id}/")
    assert response.data["reminders_enabled"] is False


def test_organizer_can_enable_reminders(anna, trip):
    response = make_client(anna).patch(
        f"/api/trips/{trip.id}/", {"reminders_enabled": True}, format="json"
    )
    assert response.status_code == 200
    trip.refresh_from_db()
    assert trip.reminders_enabled is True


def test_participant_cannot_change_reminders(ivan, trip):
    response = make_client(ivan).patch(
        f"/api/trips/{trip.id}/", {"reminders_enabled": True}, format="json"
    )
    assert response.status_code == 403