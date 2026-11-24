from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from trips.models import Trip, TripMember


class Expense(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    paid_by = models.ForeignKey(
        TripMember,
        on_delete=models.RESTRICT,
        related_name="paid_expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ExpenseShare(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="shares",
    )
    member = models.ForeignKey(
        TripMember,
        on_delete=models.RESTRICT,
        related_name="expense_shares",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["expense", "member"],
                name="unique_expense_share",
            )
        ]

    def __str__(self):
        return f"{self.member}: {self.amount}"
