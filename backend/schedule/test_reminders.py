from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from schedule.models import ScheduleItem
from trips.models import Trip, TripMember

User = get_user_model()


@pytest.fixture
def trip(db):
    anna = User.objects.create_user(
        username="anna", password="StrongPass123", email="anna@example.com"
    )
    ivan = User.objects.create_user(
        username="ivan", password="StrongPass123", email="ivan@example.com"
    )
    trip = Trip.objects.create(
        title="Lviv",
        start_date="2026-12-01",
        end_date="2026-12-03",
        reminders_enabled=True,
    )
    TripMember.objects.create(trip=trip, user=anna, role=TripMember.Role.ORGANIZER)
    TripMember.objects.create(trip=trip, user=ivan)
    return trip


def make_item(trip, hours):
    start = timezone.now() + timedelta(hours=hours)
    return ScheduleItem.objects.create(
        trip=trip, title="Museum", start=start, end=start + timedelta(hours=1)
    )


def test_sends_email_to_all_members(trip):
    make_item(trip, 5)
    call_command("send_reminders")
    assert len(mail.outbox) == 1
    assert set(mail.outbox[0].to) == {"anna@example.com", "ivan@example.com"}


def test_does_not_send_twice(trip):
    make_item(trip, 5)
    call_command("send_reminders")
    call_command("send_reminders")
    assert len(mail.outbox) == 1


def test_skips_when_reminders_disabled(trip):
    trip.reminders_enabled = False
    trip.save()
    make_item(trip, 5)
    call_command("send_reminders")
    assert len(mail.outbox) == 0


def test_skips_items_far_in_future(trip):
    make_item(trip, 72)
    call_command("send_reminders")
    assert len(mail.outbox) == 0