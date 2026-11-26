from django.utils import timezone
from rest_framework import serializers

from ideas.models import Idea

from .models import Poll, PollOption


class PollOptionSerializer(serializers.ModelSerializer):
    idea_title = serializers.CharField(source="idea.title", read_only=True)
    votes_count = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = ["id", "idea", "idea_title", "votes_count"]

    def get_votes_count(self, obj):
        return obj.votes.count()


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    idea_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, min_length=2
    )
    my_vote = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            "id",
            "trip",
            "title",
            "deadline",
            "status",
            "winner",
            "created_at",
            "options",
            "idea_ids",
            "my_vote",
            "total_votes",
        ]
        read_only_fields = ["id", "trip", "status", "winner", "created_at"]

    def get_my_vote(self, obj):
        user = self.context["request"].user
        vote = obj.votes.filter(user=user).first()
        return vote.option_id if vote else None

    def get_total_votes(self, obj):
        return obj.votes.count()

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Дедлайн має бути в майбутньому")
        return value

    def validate_idea_ids(self, value):
        trip = self.context["trip"]
        ideas = Idea.objects.filter(trip=trip, id__in=value)
        if ideas.count() != len(set(value)):
            raise serializers.ValidationError("Ідеї мають належати цій поїздці")
        return list(set(value))

    def create(self, validated_data):
        idea_ids = validated_data.pop("idea_ids")
        poll = Poll.objects.create(**validated_data)
        for idea_id in idea_ids:
            PollOption.objects.create(poll=poll, idea_id=idea_id)
        return poll


class VoteInputSerializer(serializers.Serializer):
    option = serializers.IntegerField()


class CloseInputSerializer(serializers.Serializer):
    winner_option = serializers.IntegerField(required=False)