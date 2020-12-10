from django.http import JsonResponse, HttpResponseNotFound, HttpResponse

from events.serializers import EventSerializer
from requirements.requirements_checker import RequirementsChecker
from users.users_service import UsersService
from events.events_repository import EventsRepository


def does_user_meet_requirements(event, user):
    return RequirementsChecker(event.requirements).check(user)


def get_events(request):
    jwt = request.headers['Authorization']
    users_service = UsersService()
    user = users_service.fetch_by_jwt(jwt)
    events_repository = EventsRepository()
    events = events_repository.find_events_for_given_with_respect_to_filters(dict(price=12.12))
    available_events = list(filter(lambda event: does_user_meet_requirements(event, user), events))
    serializer = EventSerializer(available_events, context=dict(user=user), many=True)
    response = serializer.data
    return JsonResponse(response, safe=False)
