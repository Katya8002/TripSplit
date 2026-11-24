from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from trips.models import TripMember

from .models import Expense, ExpenseShare


class ExpenseShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseShare
        fields = ["id", "member", "amount"]


class ExpenseSerializer(serializers.ModelSerializer):
    shares = ExpenseShareSerializer(many=True, read_only=True)

    participants = serializers.PrimaryKeyRelatedField(
        queryset=TripMember.objects.all(),
        many=True,
        write_only=True,
        allow_empty=False,
    )

    class Meta:
        model = Expense
        fields = [
            "id",
            "trip",
            "title",
            "amount",
            "paid_by",
            "participants",
            "shares",
            "created_at",
        ]
        read_only_fields = ["id", "trip", "created_at"]

    def validate(self, attrs):
        trip = self.context["trip"]
        participants = attrs["participants"]

        if attrs["paid_by"].trip_id != trip.id:
            raise serializers.ValidationError(
                "Payer must be a member of this trip."
            )

        for member in participants:
            if member.trip_id != trip.id:
                raise serializers.ValidationError(
                    "All participants must belong to this trip."
                )

        if len(set(participants)) != len(participants):
            raise serializers.ValidationError(
                "Participants must not be duplicated."
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        participants = validated_data.pop("participants")

        expense = Expense.objects.create(
            trip=self.context["trip"],
            **validated_data,
        )

        cents = int(expense.amount * 100)

        share, remainder = divmod(
            cents, len(participants)
        )

        for index, member in enumerate(participants):
            amount = share

            if index < remainder:
                amount += 1

            ExpenseShare.objects.create(
                expense=expense,
                member=member,
                amount=Decimal(amount) / 100,
            )

        return expense