import datetime
import typing

OPTIONAL_DT = typing.Optional[datetime.datetime]


class OpenhabPersistenceData:

    def __init__(self):
        self.data: typing.Dict[float, typing.Union[int, float, str]] = {}

    @classmethod
    def from_dict(cls, data) -> 'OpenhabPersistenceData':
        c = cls()
        for entry in data['data']:
            # calc as timestamp
            time = entry['time'] / 1000
            state = entry['state']
            if '.' in state:
                try:
                    state = float(state)
                except ValueError:
                    pass
            else:
                try:
                    state = int(state)
                except ValueError:
                    pass

            c.data[time] = state
        return c

    def get_data(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None):
        if start_date is None and end_date is None:
            return self.data

        filter_start = start_date.timestamp() if start_date else None
        filter_end = end_date.timestamp() if end_date else None

        ret = {}
        for ts, val in self.data.items():
            if filter_start is not None and ts < filter_start:
                continue
            if filter_end is not None and ts > filter_end:
                continue
            ret[ts] = val
        return ret

    def min(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> typing.Optional[float]:
        return min(self.get_data(start_date, end_date).values(), default=None)

    def max(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> typing.Optional[float]:
        return max(self.get_data(start_date, end_date).values(), default=None)

    def average(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> typing.Optional[float]:
        values = list(self.get_data(start_date, end_date).values())
        ct = len(values)
        if ct == 0:
            return None
        return sum(values) / ct
