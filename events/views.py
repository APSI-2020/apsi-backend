from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from events.events_repository import EventsRepository
from events.serializers import EventSerializer
from requirements.requirements_checker import RequirementsChecker
from users.users_service import UsersService


def does_user_meet_requirements(event, user):
    return RequirementsChecker(event.requirements).check(user)


class Events(APIView):
    events_response = openapi.Response('response description', EventSerializer(many=True))
    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authorization token which starts with Bearer", type=openapi.TYPE_STRING)
    price = openapi.Parameter('price', openapi.IN_QUERY, description="Returns events with lower or equal price", type=openapi.FORMAT_FLOAT)
    date_from = openapi.Parameter('date_from', openapi.IN_QUERY, description="Returns events that started after given datetime", type=openapi.FORMAT_DATETIME)
    date_to = openapi.Parameter('date_to', openapi.IN_QUERY, description="Returns events that ended before given datetime", type=openapi.FORMAT_DATETIME)
    name_contains = openapi.Parameter('name_contains', openapi.IN_QUERY, description="Returns events that contain given name", type=openapi.TYPE_STRING)
    past_events = openapi.Parameter('past_events', openapi.IN_QUERY, description="Returns also events that already ended", type=openapi.TYPE_STRING)
    place = openapi.Parameter('place', openapi.IN_QUERY, description="Returns events that are happening at given place", type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for retrieving filtered events.',
                         responses={200: events_response, 404: []},
                         manual_parameters=[authorization_token, price, date_from, date_to, name_contains, past_events, place])
    def get(self, request):
        jwt = request.headers['Authorization']
        users_service = UsersService()
        user = users_service.fetch_by_jwt(jwt)
        events_repository = EventsRepository()
        events = events_repository.find_events_for_given_with_respect_to_filters(self)
        available_events = list(filter(lambda event: does_user_meet_requirements(event, user), events))
        serializer = EventSerializer(available_events, context=dict(user=user), many=True)
        response = serializer.data
        return JsonResponse(response, safe=False)
