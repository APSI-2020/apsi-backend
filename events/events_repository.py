from datetime import datetime

from dateutil.parser import parse
from django.db.models import Q

from events.models import Events


class EventsRepository:
    def __init__(self):
        pass

    def find_events_for_given_with_respect_to_filters(self, request, user):
        filters = dict(request.request.GET)
        query = Events.objects
        date_from = filters.get('date_from', None)
        date_to = filters.get('date_to', None)
        name_contains = filters.get('name_contains', None)
        tags = filters.get('tags', None)
        past_events = filters.get('past_events', None)
        price = filters.get('price', None)
        place = filters.get('place', None)
        user_signed_up = filters.get('user_signed_up', None)

        if price is not None:
            query = query.filter(price__lte=float(price[0]))

        if place:
            query = query.filter(place__name__icontains=place[0])

        if name_contains:
            query = query.filter(name__icontains=name_contains[0])

        if user_signed_up is not None:
            user_signed_up = user_signed_up[0] == 'true'
            if user_signed_up:
                query = query.filter(participants=user.id)

        if date_from or date_to:
            if date_from and date_to:
                datetime_start = parse(date_from[0])
                datetime_end = parse(date_to[0])
                query = query.filter(start__gte=datetime_start, end__lte=datetime_end)

            elif date_from:
                datetime_start = parse(date_from[0])
                date_filter = Q(start__date__gte=datetime_start)
                time_filter = Q(start__time__gte=datetime_start)
                query = query.filter(date_filter & time_filter)

            else:
                datetime_end = parse(date_to[0])
                date_filter = Q(end__date__lte=datetime_end)
                time_filter = Q(end__time__lte=datetime_end)
                query = query.filter(date_filter & time_filter)

        if tags:
            query = query.filter(tags__in=tags[0])

        if past_events is True:
            now = datetime.now()
            date_filter = Q(start__date__lte=now)
            time_filter = Q(start__time__lte=now)
            query = query.filter(date_filter & time_filter)

        return query.all()

    def get_event_by_id(self, event_id):
        event = Events.objects.get(id=event_id)
        return event

    def save(self, event_to_save):
        event_to_save.save()
        return event_to_save

    def get_events_for_given_place_and_time_brakcet(self, place_id, start_datetime, end_datetime):
        place_filter = Q(place_id=place_id)

        # Checking if two ranges overlap is done by this formula:
        # end1 >= start2 and end2 >= start1 which equals end1 >= start2 and start1 < end2

        first_time_filter = Q(end__gte=start_datetime)
        second_time_filter = Q(start__lt=end_datetime)

        # it is not returned right away for debugging purposes
        events = Events.objects.filter(place_filter & first_time_filter & second_time_filter)
        return events
