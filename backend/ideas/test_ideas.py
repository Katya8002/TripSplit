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


def test_filter_by_category(trip, member):
    client = client_for(member)
    client.post(f"/api/trips/{trip.id}/ideas/", {"title": "Cafe", "category": "food"})
    client.post(f"/api/trips/{trip.id}/ideas/", {"title": "Park", "category": "nature"})
    response = client.get(f"/api/trips/{trip.id}/ideas/?category=food")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Cafe"


def test_filter_by_price(trip, member):
    client = client_for(member)
    client.post(f"/api/trips/{trip.id}/ideas/", {"title": "Cheap", "price": "10"})
    client.post(f"/api/trips/{trip.id}/ideas/", {"title": "Pricey", "price": "100"})
    response = client.get(f"/api/trips/{trip.id}/ideas/?price_max=50")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Cheap"


def create_idea(client, trip):
    response = client.post(f"/api/trips/{trip.id}/ideas/", {"title": "Cafe"})
    return response.data["id"]


def test_like_idea(trip, member):
    client = client_for(member)
    idea_id = create_idea(client, trip)
    response = client.post(
        f"/api/trips/{trip.id}/ideas/{idea_id}/react/", {"value": 1}
    )
    assert response.status_code == 200
    assert response.data["likes_count"] == 1
    assert response.data["my_reaction"] == 1


def test_repeated_reaction_replaces_previous(trip, member):
    client = client_for(member)
    idea_id = create_idea(client, trip)
    url = f"/api/trips/{trip.id}/ideas/{idea_id}/react/"
    client.post(url, {"value": 1})
    response = client.post(url, {"value": -1})
    assert response.data["likes_count"] == 0
    assert response.data["dislikes_count"] == 1
    assert response.data["my_reaction"] == -1


def test_invalid_reaction_value(trip, member):
    client = client_for(member)
    idea_id = create_idea(client, trip)
    response = client.post(
        f"/api/trips/{trip.id}/ideas/{idea_id}/react/", {"value": 5}
    )
    assert response.status_code == 400


def test_stranger_cannot_react(trip, member, stranger):
    idea_id = create_idea(client_for(member), trip)
    response = client_for(stranger).post(
        f"/api/trips/{trip.id}/ideas/{idea_id}/react/", {"value": 1}
    )
    assert response.status_code == 404