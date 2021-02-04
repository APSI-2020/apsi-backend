from events.events_repository import EventsRepository


class PlaceChecker:
    events_repository = EventsRepository()

    def __init__(self, place_id):
        self.place_id = place_id

    def check_if_place_available(self, start_datetime, end_datetime):
        events = self.events_repository.get_events_for_given_place_and_time_brakcet(
            self.place_id, start_datetime, end_datetime)

        if events:
            return False
        else:
            return True
