from copy import deepcopy

from dateutil.parser import parse
from django.http import FileResponse
from django.http import JsonResponse, HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from events.cyclic_event_generator import CyclicEventGenerator
from events.events_repository import EventsRepository
from events.events_service import EventsService
from events.models import Places as ModelPlaces
from events.place_checker import PlaceChecker
from events.serializers import EventSerializer, CreateEventSerializer, PlaceSerializer, CreatePlaceSerializer
from events.serializers import user_paid_for_event
from events.ticket_pdf_generator import TicketPdfGenerator
from users.users_service import UsersService


def is_place_free_in_time_bracket(place_id, start_datetime, end_datetime):
    return PlaceChecker(place_id).check_if_place_available(start_datetime, end_datetime)


def is_start_and_end_in_the_same_day_and_in_right_order(start_datetime, end_datetime):
    start = parse(start_datetime)
    end = parse(end_datetime)
    return start.date() == end.date() and start < end


def is_cyclic_boundary_after_event_end(end_datetime, cyclic_boundary):
    boundary = parse(cyclic_boundary)
    end = parse(end_datetime)

    return end.date() != boundary.date() and end < boundary


def place_is_free_for_cyclic_event(cyclic_events_data):
    if len(cyclic_events_data) == 0:
        return True

    for event_data in cyclic_events_data:
        place_id = event_data['place']
        start_datetime = event_data['start']
        end_datetime = event_data['end']

        if not is_place_free_in_time_bracket(place_id, start_datetime, end_datetime):
            return False

    return True


class Events(APIView):
    cyclic_events_generator = CyclicEventGenerator()
    events_repository = EventsRepository()
    users_service = UsersService()
    events_service = EventsService()
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

    user_is_assigned_lecturer = openapi.Parameter('user_is_assigned_lecturer', openapi.IN_QUERY,
                                                  description="Returns only those events that user is assigned as lecturer",
                                                  type=openapi.TYPE_BOOLEAN, default=False)

    only_not_cyclical_and_roots = openapi.Parameter('only_not_cyclical_and_roots', openapi.IN_QUERY,
                                                    description="Returns only those events that are not cyclical or are cyclic events roots",
                                                    type=openapi.TYPE_BOOLEAN, default=False)

    @swagger_auto_schema(operation_description='Endpoint for retrieving filtered events.',
                         responses={200: events_response, 404: []},
                         manual_parameters=[authorization_token, price, date_from, date_to, name_contains, past_events,
                                            place, user_signed_up, user_is_assigned_lecturer,
                                            only_not_cyclical_and_roots])
    def get(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        events = self.events_repository.find_events_for_given_with_respect_to_filters(self, user)
        available_events = list(
            filter(lambda event: self.events_service.does_user_meet_requirements(event, user), events))
        serializer = EventSerializer(available_events, context=dict(user=user), many=True)
        response = serializer.data
        return JsonResponse(response, safe=False)

    @swagger_auto_schema(request_body=CreateEventSerializer, operation_description='Endpoint for adding event.',
                         manual_parameters=[authorization_token],
                         responses={200: 'id',
                                    403: 'Only lecturers can create events',
                                    400: 'Frequency of event occurrence must be defined',
                                    409: 'This place is already booked for given time bracket'
                                    })
    def put(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)

        if not user.groups.filter(name='Lecturer').exists():
            return JsonResponse(data={"error": "Only lecturers can create events."},
                                status=status.HTTP_403_FORBIDDEN,
                                safe=False)

        frequency = request.data.get('frequency', None)
        place_id = request.data.get('place', None)
        start_datetime = request.data.get('start', None)
        end_datetime = request.data.get('end', None)

        if frequency is None or frequency not in ['ONCE', 'DAILY', 'WEEKLY', 'MONTHLY'] \
                or place_id is None or start_datetime is None or end_datetime is None:
            return JsonResponse(data={"error": "One of the parameters is not defined"},
                                status=status.HTTP_400_BAD_REQUEST,
                                safe=False)

        if not is_place_free_in_time_bracket(place_id, start_datetime, end_datetime):
            return JsonResponse(data={"error": "This place is already booked for given time"},
                                status=status.HTTP_409_CONFLICT,
                                safe=False)

        if not is_start_and_end_in_the_same_day_and_in_right_order(start_datetime, end_datetime):
            return JsonResponse(data={
                "error": "Event must start and end on the same day and the start must be before end of the event "},
                status=status.HTTP_400_BAD_REQUEST,
                safe=False)

        if frequency == 'ONCE':
            serializer = CreateEventSerializer(data=request.data, context=dict(root=None, is_cyclic=False, user=user))

            if serializer.is_valid(raise_exception=True):
                event_to_save = serializer.save()
                id = self.events_repository.save(event_to_save).pk
                return JsonResponse({'id': id}, safe=False)
            return HttpResponseBadRequest()

        else:
            cyclic_boundary = request.data.get('cyclic_boundary', None)

            if not is_cyclic_boundary_after_event_end(end_datetime, cyclic_boundary):
                return JsonResponse(data={"error": "Cyclic boundary cant be before events end"},
                                    status=status.HTTP_400_BAD_REQUEST,
                                    safe=False)

            # Creating root
            serializer = CreateEventSerializer(data=request.data, context=dict(root=None, is_cyclic=True, user=user))
            if serializer.is_valid(raise_exception=True):
                root_event = serializer.save()

            data_copy = deepcopy(request.data)
            cyclic_events = self.cyclic_events_generator.generate_events(data_copy)
            for event in cyclic_events:
                print(event)

            if not place_is_free_for_cyclic_event(cyclic_events):
                root_event.delete()

                return JsonResponse(data={"error": "This place is already booked for given time"},
                                    status=status.HTTP_409_CONFLICT,
                                    safe=False)
            else:
                serializer = CreateEventSerializer(data=cyclic_events, many=True,
                                                   context=dict(root=root_event, is_cyclic=True, user=user))

                if serializer.is_valid(raise_exception=True):
                    events_to_save = serializer.save()
                    events_ids = [root_event.id]
                    events_ids.extend([event.id for event in events_to_save])
                    return JsonResponse({'ids': events_ids}, safe=False)
                else:
                    root_event.delete()

                return HttpResponseBadRequest()


class Event(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()
    events_service = EventsService()

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
        if not self.events_service.does_user_meet_requirements(event, user):
            return JsonResponse(dict(error="User does not meet requirements to preview this event"),
                                status=status.HTTP_404_NOT_FOUND, safe=False)
        serializer = EventSerializer(event, context=dict(user=user), many=False)
        response = serializer.data
        return JsonResponse(response, safe=False)


class JoinEvent(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()
    events_service = EventsService()

    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for joining to event.',
                         manual_parameters=[authorization_token])
    def post(self, request, event_id):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        event = self.events_repository.get_event_by_id(event_id)
        return self.events_service.join(user, event)


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


class Ticket(APIView):
    events_repository = EventsRepository()
    users_service = UsersService()
    ticket_pdf_generator = TicketPdfGenerator()

    file_response = openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE))
    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for retrieving ticket',
                         responses={200: file_response, 403: None},
                         manual_parameters=[authorization_token])
    def get(self, request, event_id):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)
        event = self.events_repository.get_event_by_id(event_id)

        if not event.is_participant(user):
            return JsonResponse(data={'error': 'User is not a participant'}, status=status.HTTP_403_FORBIDDEN,
                                safe=False)

        if event.price is not None:
            if not user_paid_for_event(user, event):
                return JsonResponse(data={'error': 'The participant did not pay for the ticket'},
                                    status=status.HTTP_403_FORBIDDEN,
                                    safe=False)

        pdf = self.ticket_pdf_generator.generate(user, event)

        return FileResponse(pdf, as_attachment=True, filename='ticket.pdf')
