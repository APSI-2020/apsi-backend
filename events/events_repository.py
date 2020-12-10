from events.models import Events
import time


class EventsRepository:
    def __init__(self):
        pass

    def find_events_for_given_with_respect_to_filters(self, filters):
        query = Events.objects
        date_from = filters.get('date_from', None)
        date_to = filters.get('date_to', None)
        name_contains = filters.get('name_contains', None)
        tags = filters.get('tags', None)
        past_events = filters.get('past_events', None)
        price = filters.get('price', None)
        place = filters.get('place', None)

        if date_from:
            query = query.filter(start__gte=date_from)
        if date_to:
            query = query.filter(end__lte=date_to)
        if name_contains:
            query = query.filter(name__icontains=name_contains)
        if tags:
            query = query.filter(tags__in=tags)
        if past_events:
            query = query.filter(end__lte=time.localtime())
        if price:
            query = query.filter(price__lte=price)
        if place:
            query = query.filter(place=place)

        return query.all()
