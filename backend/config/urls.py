from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("trips.urls")),
    path('api/', include('ideas.urls')),
    path("api/", include("schedule.urls")),
    path("api/", include("expenses.urls")),
    path('api/', include('polls.urls')),
]
