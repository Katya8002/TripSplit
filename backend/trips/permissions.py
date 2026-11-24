from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import TripMember


class IsOrganizerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.members.filter(
            user=request.user, role=TripMember.Role.ORGANIZER
        ).exists()