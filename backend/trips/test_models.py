import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from trips.models import Trip, TripMember

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="anna", password="pass12345")


@pytest.fixture
def trip(db):
    return Trip.objects.create(
        title="Lviv", start_date="2026-12-01", end_date="2026-12-03"
    )


def test_trip_str(trip):
    assert str(trip) == "Lviv"


def test_member_default_role_is_participant(trip, user):
    member = TripMember.objects.create(trip=trip, user=user)
    assert member.role == TripMember.Role.PARTICIPANT


def test_user_cannot_join_trip_twice(trip, user):
    TripMember.objects.create(trip=trip, user=user)
    with pytest.raises(IntegrityError):
        TripMember.objects.create(trip=trip, user=user)