from rest_framework import serializers

from .models import Idea, IdeaReaction


class IdeaSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()

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
            "likes_count",
            "dislikes_count",
            "my_reaction",
        ]
        read_only_fields = ["id", "trip", "author", "status", "created_at"]

    def get_likes_count(self, obj):
        return obj.reactions.filter(value=IdeaReaction.Value.LIKE).count()

    def get_dislikes_count(self, obj):
        return obj.reactions.filter(value=IdeaReaction.Value.DISLIKE).count()

    def get_my_reaction(self, obj):
        user = self.context["request"].user
        reaction = obj.reactions.filter(user=user).first()
        return reaction.value if reaction else None


class ReactionSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=IdeaReaction.Value.values)