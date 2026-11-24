from rest_framework import serializers

from .models import ScheduleItem


class ScheduleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleItem
        fields = ("id", "trip", "idea", "title", "description", "location", "start", "end")
        read_only_fields = ("trip",)

    def validate(self, data):
        start = data.get("start", getattr(self.instance, "start", None))
        end = data.get("end", getattr(self.instance, "end", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end": "Час завершення не може бути раніше за час початку"}
            )
        idea = data.get("idea")
        if idea and idea.trip_id != self.context["trip"].id:
            raise serializers.ValidationError(
                {"idea": "Ця ідея належить іншій поїздці"}
            )
        return data