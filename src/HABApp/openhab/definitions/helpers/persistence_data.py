from datetime import datetime
from typing import Optional

from fastnumbers import try_real

from HABApp.openhab.definitions.rest import ItemHistoryResp


OPTIONAL_DT = Optional[datetime]


class OpenhabPersistenceData:

    def __init__(self) -> None:
        self.data: dict[float, int | float | str] = {}

    @classmethod
    def from_resp(cls, data: ItemHistoryResp) -> 'OpenhabPersistenceData':
        c = cls()
        for entry in data.data:
            # calc as timestamp
            time = entry.time / 1000
            c.data[time] = try_real(entry.state)
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

    def min(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> float | None:
        return min(self.get_data(start_date, end_date).values(), default=None)

    def max(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> float | None:
        return max(self.get_data(start_date, end_date).values(), default=None)

    def average(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> float | None:
        values = list(self.get_data(start_date, end_date).values())
        ct = len(values)
        if ct == 0:
            return None
        return sum(values) / ct
