import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from schedule.models import ScheduleItem
from trips.models import Trip, TripMember

User = get_user_model()

DATA = {
    "title": "Museum",
    "start": "2026-12-01T10:00:00Z",
    "end": "2026-12-01T12:00:00Z",
}


def make_client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


@pytest.fixture
def anna(db):
    return User.objects.create_user(username="anna", password="StrongPass123")


@pytest.fixture
def ivan(db):
    return User.objects.create_user(username="ivan", password="StrongPass123")


@pytest.fixture
def stranger(db):
    return User.objects.create_user(username="stranger", password="StrongPass123")


@pytest.fixture
def trip(anna, ivan):
    trip = Trip.objects.create(
        title="Lviv", start_date="2026-12-01", end_date="2026-12-03"
    )
    TripMember.objects.create(trip=trip, user=anna, role=TripMember.Role.ORGANIZER)
    TripMember.objects.create(trip=trip, user=ivan)
    return trip


def url(trip):
    return f"/api/trips/{trip.id}/schedule/"


def test_organizer_can_create_item(anna, trip):
    response = make_client(anna).post(url(trip), DATA, format="json")
    assert response.status_code == 201
    assert ScheduleItem.objects.filter(trip=trip).count() == 1


def test_participant_can_read_but_not_create(anna, ivan, trip):
    make_client(anna).post(url(trip), DATA, format="json")
    response = make_client(ivan).get(url(trip))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert make_client(ivan).post(url(trip), DATA, format="json").status_code == 403


def test_stranger_gets_404(stranger, trip):
    assert make_client(stranger).get(url(trip)).status_code == 404


def test_anonymous_gets_401(trip):
    assert make_client().get(url(trip)).status_code == 401


def test_end_before_start_rejected(anna, trip):
    data = {**DATA, "start": DATA["end"], "end": DATA["start"]}
    response = make_client(anna).post(url(trip), data, format="json")
    assert response.status_code == 400


def test_items_sorted_by_start(anna, trip):
    later = {**DATA, "title": "Later", "start": "2026-12-02T10:00:00Z", "end": "2026-12-02T11:00:00Z"}
    make_client(anna).post(url(trip), later, format="json")
    make_client(anna).post(url(trip), DATA, format="json")
    titles = [item["title"] for item in make_client(anna).get(url(trip)).data]
    assert titles == ["Museum", "Later"]


def test_participant_cannot_delete(anna, ivan, trip):
    item_id = make_client(anna).post(url(trip), DATA, format="json").data["id"]
    response = make_client(ivan).delete(f"{url(trip)}{item_id}/")
    assert response.status_code == 403