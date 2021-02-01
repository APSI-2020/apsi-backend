from django.http import JsonResponse, HttpResponse

from events.events_repository import EventsRepository
from events.serializers import EventSerializer
from requirements.requirements_checker import RequirementsChecker
from rest_framework import status


class EventsService:
    def __init__(self):
        self.events_repository = EventsRepository()

    def join(self, user, event):
        if event.is_cyclic:
            if event.root:
                cyclic_events = self.events_repository.find_all_cyclic_events_for_given_root(event.root)
            else:
                cyclic_events = self.events_repository.find_all_cyclic_events_for_given_root(event)

            validations = [self.can_join(user, e) for e in cyclic_events]

            if self.there_are_failures(validations):
                return validations[0]
            else:
                [self.join_event(e, user) for e in cyclic_events]
                return HttpResponse(status=status.HTTP_201_CREATED)

        validation = self.can_join(user, event)
        if type(validation) is not JsonResponse:
            return self.join_event(event, user)
        else:
            return validation

    def there_are_failures(self, validations):
        return len(list(filter(lambda x: x is True, validations))) != len(validations)

    def join_event(self, event, user):
        event.number_of_participants = event.number_of_participants + 1
        event.participants.add(user)
        event.save()
        return HttpResponse(status=status.HTTP_201_CREATED)

    def can_join(self, user, event):
        serialized_event = EventSerializer(event, context=dict(user=user), many=False).data
        if serialized_event['limit_of_participants'] <= serialized_event['amount_of_participants']:
            return JsonResponse(dict(error='Event is full.'), safe=False, status=400)

        if serialized_event['is_signed_up_for']:
            return JsonResponse(dict(error='User is already signed up for this event'), safe=False, status=400)

        if not self.does_user_meet_requirements(event, user):
            return JsonResponse(dict(error='User does not meet requirements'), safe=False, status=400)

        return True

    def does_user_meet_requirements(self, event, user):
        return RequirementsChecker(event.requirements).check(user)
