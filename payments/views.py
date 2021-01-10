from django.http import JsonResponse, HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from events.events_repository import EventsRepository
from users.users_service import UsersService
from .payments_repository import PaymentsRepository
from .serializers import CreatePaymentSerializer, PaymentURLSerializer


class Payments(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()
    payments_repository = PaymentsRepository()

    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for confirming payments.',
                         request_body=CreatePaymentSerializer,
                         manual_parameters=[authorization_token],
                         responses={404: None, 202: 'Payment confirmed', 403: 'User is not a participant',
                                    409: 'User already payed', 405: 'Event does not require payment',
                                    406: 'Payment not sufficient'},

                         )
    def post(self, request):
        jwt = request.headers['Authorization']
        event_id = request.data['event_id']

        user = self.users_service.fetch_by_jwt(jwt)
        event = self.events_repository.get_event_by_id(event_id)

        payment = self.payments_repository.get_payment_for_user_and_event(user, event)

        if not event:
            return JsonResponse(data=None, status=status.HTTP_404_NOT_FOUND, safe=False)
        if event.price is None:
            return JsonResponse(data='Event does not require payment', status=status.HTTP_405_METHOD_NOT_ALLOWED,
                                safe=False)
        if payment:
            return JsonResponse(data='User already payed', status=status.HTTP_409_CONFLICT, safe=False)
        if not event.participants.filter(id=user.id):
            return JsonResponse(data='User is not a participant', status=status.HTTP_403_FORBIDDEN, safe=False)

        serializer = CreatePaymentSerializer(data=request.data, context=dict(user=user, event=event, price=event.price))

        if serializer.is_valid(raise_exception=True):
            payment_to_save = serializer.save()
            self.events_repository.save(payment_to_save)
            return JsonResponse(data='Payment confirmed', status=status.HTTP_202_ACCEPTED, safe=False)
        return HttpResponseBadRequest()


class PaymentsURL(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()
    payments_repository = PaymentsRepository()

    payment_url_response = openapi.Response('response description', PaymentURLSerializer)

    event_id = openapi.Parameter('event_id', openapi.IN_QUERY, description="Event id",
                                 type=openapi.TYPE_INTEGER)

    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for acquiring urls for payments.',
                         manual_parameters=[authorization_token, event_id],
                         responses={404: None, 200: payment_url_response, 409: 'Payment already made',
                                    405: 'Event does not require payment', 403: 'User is not a participant'},

                         )
    def get(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        request_data = dict(request.GET)
        event_id = request_data.get('event_id', None)

        if event_id is None:
            return JsonResponse(data=None, status=status.HTTP_404_NOT_FOUND, safe=False)

        event_id = int(event_id[0])

        event = self.events_repository.get_event_by_id(event_id)

        payment = self.payments_repository.get_payment_for_user_and_event(user, event)

        if not event:
            return JsonResponse(data=None, status=status.HTTP_404_NOT_FOUND, safe=False)
        if event.price is None:
            return JsonResponse(data='Event does not require payment', status=status.HTTP_405_METHOD_NOT_ALLOWED,
                                safe=False)
        if payment:
            return JsonResponse(data='User already payed', status=status.HTTP_409_CONFLICT, safe=False)
        if not event.participants.filter(id=user.id):
            return JsonResponse(data='User is not a participant', status=status.HTTP_403_FORBIDDEN, safe=False)

        serializer = PaymentURLSerializer({'event_id': event_id, 'price': event.price})
        response = serializer.data
        return JsonResponse(response, safe=False)
