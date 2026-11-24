from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from trips.models import Trip, TripMember

from .models import Expense


@pytest.fixture
def trip_data(django_user_model):
    trip = Trip.objects.create(
        title="Vienna",
        start_date=date(2027, 1, 2),
        end_date=date(2027, 1, 10),
    )

    members = []

    for username in ["user1", "user2", "user3"]:
        user = django_user_model.objects.create_user(
            username=username,
        )
        member = TripMember.objects.create(
            trip=trip,
            user=user,
        )
        members.append(member)

    client = APIClient()
    token = AccessToken.for_user(members[0].user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    url = f"/api/trips/{trip.id}/expenses/"

    return client, url, members


@pytest.mark.django_db
def test_create_expense(trip_data):
    client, url, members = trip_data

    response = client.post(url, {
        "title": "Dinner",
        "amount": "300.00",
        "paid_by": members[0].id,
        "participants": [member.id for member in members],
    }, format="json")

    assert response.status_code == 201

    expense = Expense.objects.get()

    assert expense.amount == Decimal("300.00")
    assert expense.shares.count() == 3

    for share in expense.shares.all():
        assert share.amount == Decimal("100.00")


@pytest.mark.django_db
def test_expense_rounding(trip_data):
    client, url, members = trip_data

    response = client.post(url, {
        "title": "Taxi",
        "amount": "100.00",
        "paid_by": members[0].id,
        "participants": [member.id for member in members],
    }, format="json")

    assert response.status_code == 201

    expense = Expense.objects.get()

    amounts = sorted(
        share.amount for share in expense.shares.all()
    )

    assert amounts == [
        Decimal("33.33"),
        Decimal("33.33"),
        Decimal("33.34"),
    ]
    assert sum(amounts) == expense.amount


@pytest.mark.django_db
def test_list_expenses(trip_data):
    client, url, members = trip_data

    Expense.objects.create(
        trip=members[0].trip,
        title="Hotel",
        amount=Decimal("500.00"),
        paid_by=members[0],
    )

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Hotel"


@pytest.mark.django_db
def test_negative_amount(trip_data):
    client, url, members = trip_data

    response = client.post(url, {
        "title": "Dinner",
        "amount": "-100.00",
        "paid_by": members[0].id,
        "participants": [members[0].id],
    }, format="json")

    assert response.status_code == 400
    assert Expense.objects.count() == 0


@pytest.mark.django_db
def test_duplicate_participants(trip_data):
    client, url, members = trip_data

    response = client.post(url, {
        "title": "Dinner",
        "amount": "100.00",
        "paid_by": members[0].id,
        "participants": [members[0].id, members[0].id],
    }, format="json")

    assert response.status_code == 400
    assert Expense.objects.count() == 0


@pytest.mark.django_db
def test_unauthenticated_access(trip_data):
    _, url, _ = trip_data

    client = APIClient()
    response = client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_outsider_access(trip_data, django_user_model):
    _, url, members = trip_data

    user = django_user_model.objects.create_user(
        username="outsider",
    )

    client = APIClient()
    token = AccessToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    assert client.get(url).status_code == 404

    response = client.post(url, {
        "title": "Dinner",
        "amount": "100.00",
        "paid_by": members[0].id,
        "participants": [members[0].id],
    }, format="json")

    assert response.status_code == 404
    assert Expense.objects.count() == 0