from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from trips.models import Trip

from .models import Expense
from .serializers import ExpenseSerializer


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_trip(self):
        return get_object_or_404(
            Trip,
            id=self.kwargs["trip_id"],
            members__user=self.request.user,
        )

    def get_queryset(self):
        return Expense.objects.filter(
            trip=self.get_trip()
        ).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["trip"] = self.get_trip()
        return context
