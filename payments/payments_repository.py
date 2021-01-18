from django.db.models import Q

from .models import Payments


class PaymentsRepository:

    def get_payments_for_user(self, user):
        return Payments.objects.filter(user=user)

    def get_payments_for_event(self, event):
        return Payments.objects.filter(event=event)

    @staticmethod
    def get_payment_for_user_and_event(user, event):
        user_filter = Q(user=user)
        event_filter = Q(event=event)

        return Payments.objects.filter(user_filter & event_filter)

    def save(self, payment_to_save):
        payment_to_save.save()
        return payment_to_save
