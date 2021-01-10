from django.urls import path

from .views import Payments, PaymentsURL

urlpatterns = [
    path('payments/', Payments.as_view(), name="payments"),
    path('payments/get-url', PaymentsURL.as_view(), name="payments_url")
]
