from django.urls import path

from .views import IdeaViewSet

idea_list = IdeaViewSet.as_view({"get": "list", "post": "create"})
idea_detail = IdeaViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)
idea_react = IdeaViewSet.as_view({"post": "react"})

urlpatterns = [
    path("trips/<int:trip_id>/ideas/", idea_list, name="idea-list"),
    path("trips/<int:trip_id>/ideas/<int:pk>/", idea_detail, name="idea-detail"),
    path("trips/<int:trip_id>/ideas/<int:pk>/react/", idea_react, name="idea-react"),
]