from datetime import date
from decimal import Decimal

import pytest

from trips.models import Trip, TripMember

from .models import Expense, ExpenseShare


@pytest.mark.django_db
def test_create_expense(django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser",
    )

    trip = Trip.objects.create(
        title="Vienna",
        start_date=date(2027, 1, 2),
        end_date=date(2027, 1, 10),
    )

    member = TripMember.objects.create(
        trip=trip,
        user=user,
    )

    expense = Expense.objects.create(
        trip=trip,
        title="Dinner",
        amount=Decimal("300.00"),
        paid_by=member,
    )

    share = ExpenseShare.objects.create(
        expense=expense,
        member=member,
        amount=Decimal("300.00"),
    )

    assert expense.title == "Dinner"
    assert expense.amount == Decimal("300.00")
    assert expense.shares.count() == 1
    assert share.member == member