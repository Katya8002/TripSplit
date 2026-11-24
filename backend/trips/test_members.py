import uuid

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


def join(user, code):
    return make_client(user).post(f"{URL}join/", {"invite_code": code}, format="json")


def test_join_by_invite_code_adds_participant(anna, ivan):
    code = create_trip(anna).data["invite_code"]
    response = join(ivan, code)
    assert response.status_code == 201
    assert TripMember.objects.get(user=ivan).role == TripMember.Role.PARTICIPANT


def test_join_twice_does_not_duplicate(anna, ivan):
    code = create_trip(anna).data["invite_code"]
    join(ivan, code)
    response = join(ivan, code)
    assert response.status_code == 200
    assert TripMember.objects.filter(user=ivan).count() == 1


def test_join_with_unknown_code_returns_404(ivan):
    assert join(ivan, str(uuid.uuid4())).status_code == 404


def test_members_visible_to_member(anna, ivan):
    trip = create_trip(anna).data
    join(ivan, trip["invite_code"])
    response = make_client(ivan).get(f"{URL}{trip['id']}/members/")
    assert response.status_code == 200
    assert len(response.data) == 2


def test_members_hidden_from_non_member(anna, ivan):
    trip_id = create_trip(anna).data["id"]
    assert make_client(ivan).get(f"{URL}{trip_id}/members/").status_code == 404


def test_organizer_can_remove_participant(anna, ivan):
    trip = create_trip(anna).data
    join(ivan, trip["invite_code"])
    response = make_client(anna).delete(f"{URL}{trip['id']}/members/{ivan.id}/")
    assert response.status_code == 204
    assert not TripMember.objects.filter(user=ivan).exists()


def test_participant_can_leave(anna, ivan):
    trip = create_trip(anna).data
    join(ivan, trip["invite_code"])
    response = make_client(ivan).delete(f"{URL}{trip['id']}/members/{ivan.id}/")
    assert response.status_code == 204


def test_participant_cannot_remove_organizer(anna, ivan):
    trip = create_trip(anna).data
    join(ivan, trip["invite_code"])
    response = make_client(ivan).delete(f"{URL}{trip['id']}/members/{anna.id}/")
    assert response.status_code == 403


def test_organizer_cannot_be_removed(anna):
    trip = create_trip(anna).data
    response = make_client(anna).delete(f"{URL}{trip['id']}/members/{anna.id}/")
    assert response.status_code == 400