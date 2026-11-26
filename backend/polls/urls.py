from django.urls import path

from .views import PollViewSet

poll_list = PollViewSet.as_view({"get": "list", "post": "create"})
poll_detail = PollViewSet.as_view({"get": "retrieve"})
poll_vote = PollViewSet.as_view({"post": "vote"})
poll_close = PollViewSet.as_view({"post": "close"})

urlpatterns = [
    path("trips/<int:trip_id>/polls/", poll_list, name="poll-list"),
    path("trips/<int:trip_id>/polls/<int:pk>/", poll_detail, name="poll-detail"),
    path("trips/<int:trip_id>/polls/<int:pk>/vote/", poll_vote, name="poll-vote"),
    path("trips/<int:trip_id>/polls/<int:pk>/close/", poll_close, name="poll-close"),
]