from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from events.events_repository import EventsRepository
from events.serializers import EventSerializer, CreateEventSerializer
from requirements.requirements_checker import RequirementsChecker
from users.users_service import UsersService


def does_user_meet_requirements(event, user):
    return RequirementsChecker(event.requirements).check(user)


class Events(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()
    events_response = openapi.Response('response description', EventSerializer(many=True))
    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)
    price = openapi.Parameter('price', openapi.IN_QUERY, description="Returns events with lower or equal price",
                              type=openapi.FORMAT_FLOAT)
    date_from = openapi.Parameter('date_from', openapi.IN_QUERY,
                                  description="Returns events that started after given datetime (example: 2019-12-12T11:07:20+00:00)",
                                  type=openapi.FORMAT_DATETIME)
    date_to = openapi.Parameter('date_to', openapi.IN_QUERY,
                                description="Returns events that ended before given datetime (example: 2019-12-12T11:07:20+00:00)",
                                type=openapi.FORMAT_DATETIME)
    name_contains = openapi.Parameter('name_contains', openapi.IN_QUERY,
                                      description="Returns events that contain given name", type=openapi.TYPE_STRING)
    past_events = openapi.Parameter('past_events', openapi.IN_QUERY,
                                    description="Returns also events that already ended", type=openapi.TYPE_STRING)
    place = openapi.Parameter('place', openapi.IN_QUERY, description="Returns events that are happening at given place",
                              type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for retrieving filtered events.',
                         responses={200: events_response, 404: []},
                         manual_parameters=[authorization_token, price, date_from, date_to, name_contains, past_events,
                                            place])
    def get(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        events = self.events_repository.find_events_for_given_with_respect_to_filters(self)
        available_events = list(filter(lambda event: does_user_meet_requirements(event, user), events))
        serializer = EventSerializer(available_events, context=dict(user=user), many=True)
        response = serializer.data
        return JsonResponse(response, safe=False)

    @swagger_auto_schema(request_body=CreateEventSerializer, operation_description='Endpoint for adding event.',
                         manual_parameters=[authorization_token])
    def put(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        serializer = CreateEventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event_to_save = serializer.save()
            self.events_repository.save(event_to_save)
        return JsonResponse({jwt: jwt}, safe=False)

class Event(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()

    event_response = openapi.Response('response description', EventSerializer(many=False))
    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for retrieving single event given event id.',
                         responses={200: event_response, 404: None},
                         manual_parameters=[authorization_token])
    def get(self, request, event_id):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        event = self.events_repository.get_event_by_id(event_id)
        if not does_user_meet_requirements(event, user):
            return JsonResponse(data=None, status=status.HTTP_404_NOT_FOUND, safe=False)
        serializer = EventSerializer(event, context=dict(user=user), many=False)
        response = serializer.data
        return JsonResponse(response, safe=False)


