from django.urls import path

from .views import Payments

urlpatterns = [
    path('payments/<int:event_id>/', Payments.as_view(), name="payments")
]
