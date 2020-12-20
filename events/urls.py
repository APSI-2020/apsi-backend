from django.urls import path

from .views import *

urlpatterns = [
    path('places/', Places.as_view(), name="places"),
    path('events/', Events.as_view(), name="events"),
    path('events/<int:event_id>/', Event.as_view(), name='event'),
    path('events/<int:event_id>/join', JoinEvent.as_view(), name='join_event')
]
