from rest_framework import serializers

from .models import Idea


class IdeaSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Idea
        fields = [
            "id",
            "trip",
            "author",
            "category",
            "title",
            "address",
            "latitude",
            "longitude",
            "link",
            "price",
            "duration_minutes",
            "note",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "trip", "author", "status", "created_at"]