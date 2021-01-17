from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from events.events_repository import EventsRepository
from events.models import Places as ModelPlaces
from events.serializers import EventSerializer, CreateEventSerializer, PlaceSerializer, CreatePlaceSerializer
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
    user_signed_up = openapi.Parameter('user_signed_up', openapi.IN_QUERY,
                                       description="Returns only those events that user is signed up for",
                                       type=openapi.TYPE_BOOLEAN, default=False)

    @swagger_auto_schema(operation_description='Endpoint for retrieving filtered events.',
                         responses={200: events_response, 404: []},
                         manual_parameters=[authorization_token, price, date_from, date_to, name_contains, past_events,
                                            place, user_signed_up])
    def get(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        events = self.events_repository.find_events_for_given_with_respect_to_filters(self, user)
        available_events = list(filter(lambda event: does_user_meet_requirements(event, user), events))
        serializer = EventSerializer(available_events, context=dict(user=user), many=True)
        response = serializer.data
        return JsonResponse(response, safe=False)

    @swagger_auto_schema(request_body=CreateEventSerializer, operation_description='Endpoint for adding event.',
                         manual_parameters=[authorization_token])
    def put(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)

        if not user.groups.filter(name='Lecturer').exists():
            return JsonResponse(data={"error": "Only lecturers can create events."},
                                status=status.HTTP_403_FORBIDDEN,
                                safe=False)

        serializer = CreateEventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event_to_save = serializer.save()
            id = self.events_repository.save(event_to_save).pk
            return JsonResponse({'id': id}, safe=False)
        return HttpResponseBadRequest()


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


class JoinEvent(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()

    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for joining to event.',
                         manual_parameters=[authorization_token])
    def post(self, request, event_id):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        event = self.events_repository.get_event_by_id(event_id)
        serializer = EventSerializer(event, context=dict(user=user), many=False)
        serialized_event = serializer.data

        if serialized_event['limit_of_participants'] <= serialized_event['amount_of_participants']:
            return JsonResponse(dict(error_message='Event is full.'), safe=False, status=400)

        if serialized_event['is_signed_up_for']:
            return JsonResponse(dict(error_message='User is already signed up for this event'), safe=False, status=400)

        if does_user_meet_requirements(event, user):
            event.number_of_participants = event.number_of_participants + 1
            event.participants.add(user)
            event.save()
            return HttpResponse(status=status.HTTP_201_CREATED)

        return JsonResponse(dict(error_message='User does not meet requirements'), safe=False, status=400)


class Places(APIView):
    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for retrieving all places.',
                         manual_parameters=[authorization_token])
    def get(self, request):
        serializer = PlaceSerializer(ModelPlaces.objects.all(), many=True)
        response = serializer.data
        return JsonResponse(response, safe=False)

    @swagger_auto_schema(operation_description='Endpoint for creating place.',
                         request_body=CreatePlaceSerializer,
                         manual_parameters=[authorization_token])
    def post(self, request):
        serializer = CreatePlaceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            place = serializer.save()
            place.save()
            return JsonResponse({'id': place.pk}, safe=False)
