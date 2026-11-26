from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from ideas.models import Idea
from polls.models import Poll, PollOption
from trips.models import Trip, TripMember

User = get_user_model()


@pytest.fixture
def trip(db):
    return Trip.objects.create(
        title="Odesa", start_date="2026-12-01", end_date="2026-12-05"
    )


@pytest.fixture
def organizer(trip):
    user = User.objects.create_user(username="org", password="pass12345")
    TripMember.objects.create(trip=trip, user=user, role=TripMember.Role.ORGANIZER)
    return user


@pytest.fixture
def member(trip):
    user = User.objects.create_user(username="member", password="pass12345")
    TripMember.objects.create(trip=trip, user=user)
    return user


@pytest.fixture
def stranger(db):
    return User.objects.create_user(username="stranger", password="pass12345")


@pytest.fixture
def ideas(trip, organizer):
    return [
        Idea.objects.create(trip=trip, author=organizer, title="Cafe"),
        Idea.objects.create(trip=trip, author=organizer, title="Park"),
    ]


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_poll(trip, organizer, ideas, deadline=None):
    poll = Poll.objects.create(
        trip=trip,
        title="Where?",
        deadline=deadline or timezone.now() + timedelta(days=1),
        created_by=organizer,
    )
    options = [PollOption.objects.create(poll=poll, idea=idea) for idea in ideas]
    return poll, options


def url(trip, poll, suffix=""):
    return f"/api/trips/{trip.id}/polls/{poll.id}/{suffix}"


def test_organizer_creates_poll(trip, organizer, ideas):
    deadline = (timezone.now() + timedelta(days=1)).isoformat()
    response = client_for(organizer).post(
        f"/api/trips/{trip.id}/polls/",
        {"title": "Where?", "deadline": deadline, "idea_ids": [i.id for i in ideas]},
        format="json",
    )
    assert response.status_code == 201
    assert len(response.data["options"]) == 2


def test_member_cannot_create_poll(trip, member, ideas):
    deadline = (timezone.now() + timedelta(days=1)).isoformat()
    response = client_for(member).post(
        f"/api/trips/{trip.id}/polls/",
        {"title": "Where?", "deadline": deadline, "idea_ids": [i.id for i in ideas]},
        format="json",
    )
    assert response.status_code == 403


def test_stranger_gets_404(trip, stranger):
    response = client_for(stranger).get(f"/api/trips/{trip.id}/polls/")
    assert response.status_code == 404


def test_vote(trip, organizer, member, ideas):
    poll, options = make_poll(trip, organizer, ideas)
    response = client_for(member).post(
        url(trip, poll, "vote/"), {"option": options[0].id}, format="json"
    )
    assert response.status_code == 201
    assert response.data["my_vote"] == options[0].id
    assert response.data["total_votes"] == 1


def test_double_vote_rejected(trip, organizer, member, ideas):
    poll, options = make_poll(trip, organizer, ideas)
    client = client_for(member)
    client.post(url(trip, poll, "vote/"), {"option": options[0].id}, format="json")
    response = client.post(
        url(trip, poll, "vote/"), {"option": options[1].id}, format="json"
    )
    assert response.status_code == 400


def test_vote_after_deadline_rejected(trip, organizer, member, ideas):
    poll, options = make_poll(
        trip, organizer, ideas, deadline=timezone.now() - timedelta(hours=1)
    )
    response = client_for(member).post(
        url(trip, poll, "vote/"), {"option": options[0].id}, format="json"
    )
    assert response.status_code == 400


def test_close_approves_winner(trip, organizer, member, ideas):
    poll, options = make_poll(trip, organizer, ideas)
    client_for(member).post(
        url(trip, poll, "vote/"), {"option": options[1].id}, format="json"
    )
    response = client_for(organizer).post(url(trip, poll, "close/"))
    assert response.status_code == 200
    ideas[1].refresh_from_db()
    ideas[0].refresh_from_db()
    assert ideas[1].status == "approved"
    assert ideas[0].status == "rejected"
    assert response.data["status"] == "closed"


def test_close_tie_requires_choice(trip, organizer, member, ideas):
    poll, options = make_poll(trip, organizer, ideas)
    client_for(member).post(
        url(trip, poll, "vote/"), {"option": options[0].id}, format="json"
    )
    client_for(organizer).post(
        url(trip, poll, "vote/"), {"option": options[1].id}, format="json"
    )
    client = client_for(organizer)
    response = client.post(url(trip, poll, "close/"))
    assert response.status_code == 400
    response = client.post(
        url(trip, poll, "close/"), {"winner_option": options[1].id}, format="json"
    )
    assert response.status_code == 200