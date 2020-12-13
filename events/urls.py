from django.urls import path

from .views import *

urlpatterns = [
    path('events', Events.as_view(), name="events"),
    path('events/<int:event_id>/', Event.as_view(), name='event')
]
