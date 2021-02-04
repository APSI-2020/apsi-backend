from copy import deepcopy
from datetime import timedelta

from dateutil.parser import parse


class CyclicEventGenerator:
    def __init__(self):
        pass

    def daterange(self, date1, date2, interval):
        for n in range(int((date2 - date1).days) + 1):
            if n % interval == 0:
                yield date1 + timedelta(n)

    def get_interval(self, frequency):
        switcher = {
            'DAILY': 1,
            'WEEKLY': 7,
            'MONTHLY': 30
        }
        return switcher.get(frequency, "Invalid frequency")

    def generate_events(self, request_data):
        start_date = parse(request_data['start'])
        end_date = parse(request_data['end'])
        frequency = request_data['frequency']
        interval = self.get_interval(frequency)
        cyclic_boundary = parse(request_data['cyclic_boundary'])
        diff = end_date - start_date

        return [self.with_modified_dates(request_data, timestamp, diff) for timestamp in
                self.daterange(start_date, cyclic_boundary, interval)][1:]

    def with_modified_dates(self, data, timestamp, diff):
        start_timestamp_right_format = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_timestamp_right_format = (timestamp + diff).strftime('%Y-%m-%dT%H:%M:%SZ')
        request = deepcopy(data)
        request['start'] = start_timestamp_right_format
        request['end'] = end_timestamp_right_format
        return request
