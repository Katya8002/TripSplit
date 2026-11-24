import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from trips.models import TripMember

User = get_user_model()

URL = "/api/trips/"
DATA = {"title": "Lviv", "start_date": "2026-12-01", "end_date": "2026-12-03"}


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


def create_trip(user):
    return make_client(user).post(URL, DATA, format="json")


def test_requires_auth(db):
    assert APIClient().get(URL).status_code == 401


def test_create_trip_makes_creator_organizer(anna):
    response = create_trip(anna)
    assert response.status_code == 201
    assert response.data["my_role"] == "organizer"
    assert TripMember.objects.get(user=anna).role == TripMember.Role.ORGANIZER


def test_list_shows_only_my_trips(anna, ivan):
    create_trip(anna)
    response = make_client(ivan).get(URL)
    assert response.status_code == 200
    assert response.data == []


def test_non_member_gets_404(anna, ivan):
    trip_id = create_trip(anna).data["id"]
    assert make_client(ivan).get(f"{URL}{trip_id}/").status_code == 404


def test_participant_cannot_update(anna, ivan):
    trip_id = create_trip(anna).data["id"]
    TripMember.objects.create(trip_id=trip_id, user=ivan)
    response = make_client(ivan).patch(
        f"{URL}{trip_id}/", {"title": "X"}, format="json"
    )
    assert response.status_code == 403


def test_organizer_can_update(anna):
    trip_id = create_trip(anna).data["id"]
    response = make_client(anna).patch(
        f"{URL}{trip_id}/", {"title": "Kyiv"}, format="json"
    )
    assert response.status_code == 200
    assert response.data["title"] == "Kyiv"


def test_end_date_before_start_rejected(anna):
    data = {"title": "Lviv", "start_date": "2026-12-03", "end_date": "2026-12-01"}
    response = make_client(anna).post(URL, data, format="json")
    assert response.status_code == 400