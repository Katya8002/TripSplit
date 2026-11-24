import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from trips.models import Trip, TripMember

User = get_user_model()


@pytest.fixture
def trip(db):
    return Trip.objects.create(
        title="Lviv", start_date="2026-12-01", end_date="2026-12-05"
    )


@pytest.fixture
def member(trip):
    user = User.objects.create_user(username="member", password="pass12345")
    TripMember.objects.create(trip=trip, user=user)
    return user


@pytest.fixture
def stranger(db):
    return User.objects.create_user(username="stranger", password="pass12345")


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_member_can_create_idea(trip, member):
    response = client_for(member).post(
        f"/api/trips/{trip.id}/ideas/", {"title": "Cafe", "category": "food"}
    )
    assert response.status_code == 201
    assert response.data["author"] == "member"


def test_member_can_list_ideas(trip, member):
    client = client_for(member)
    client.post(f"/api/trips/{trip.id}/ideas/", {"title": "Cafe"})
    response = client.get(f"/api/trips/{trip.id}/ideas/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_stranger_cannot_create_idea(trip, stranger):
    response = client_for(stranger).post(
        f"/api/trips/{trip.id}/ideas/", {"title": "Cafe"}
    )
    assert response.status_code == 404


def test_anonymous_cannot_access_ideas(trip):
    response = APIClient().get(f"/api/trips/{trip.id}/ideas/")
    assert response.status_code in (401, 403)