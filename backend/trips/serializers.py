from rest_framework import serializers

from .models import Trip


class TripSerializer(serializers.ModelSerializer):
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = (
            "id",
            "title",
            "description",
            "start_date",
            "end_date",
            "invite_code",
            "created_at",
            "my_role",
        )
        read_only_fields = ("invite_code", "created_at")

    def get_my_role(self, obj):
        member = obj.members.filter(user=self.context["request"].user).first()
        return member.role if member else None

    def validate(self, data):
        start = data.get("start_date", getattr(self.instance, "start_date", None))
        end = data.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "Дата завершення не може бути раніше за дату початку"}
            )
        return data