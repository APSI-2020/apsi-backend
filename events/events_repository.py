from datetime import datetime

from dateutil.parser import parse
from django.db.models import Q

from events.models import Events


class EventsRepository:
    def __init__(self):
        pass

    def find_events_for_given_with_respect_to_filters(self, request):
        filters = dict(request.GET)
        query = Events.objects
        date_from = filters.get('date_from', None)
        date_to = filters.get('date_to', None)
        name_contains = filters.get('name_contains', None)
        tags = filters.get('tags', None)
        past_events = filters.get('past_events', None)
        price = filters.get('price', None)
        place = filters.get('place', None)

        if date_from:
            datetime_start = parse(date_from[0])
            date_filter = Q(start__date__gte=datetime_start)
            time_filter = Q(start__time__gte=datetime_start)
            query = query.filter(date_filter & time_filter)

        if date_to:
            datetime_end = parse(date_to[0])
            date_filter = Q(start__date__lte=datetime_end)
            time_filter = Q(start__time__lte=datetime_end)
            query = query.filter(date_filter & time_filter)

        if name_contains:
            query = query.filter(name__icontains=name_contains[0])

        if tags:
            query = query.filter(tags__in=tags[0])

        if past_events is not None:
            if past_events is True:
                now = datetime.now()
                date_filter = Q(start__date__lte=now)
                time_filter = Q(start__time__lte=now)
                query = query.filter(date_filter & time_filter)

        if price is not None:
            query = query.filter(price__lte=float(price[0]))
        else:
            query = query.filter(price__isnull=True)

        if place:
            query = query.filter(place__name__icontains=place[0])

        return query.all()
