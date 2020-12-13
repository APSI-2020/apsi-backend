from django.urls import path
from .views import *
urlpatterns = [
    path('events', Events.as_view(), name="events"),
]