from datetime import datetime
from typing import Optional, FrozenSet, Mapping

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData


class DatetimeItem(OpenhabItem):
    """DateTimeItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar datetime value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    @classmethod
    def from_oh(cls, name: str, value=None, label: Optional[str] = None, tags: FrozenSet[str] = frozenset(),
                groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):
        if value is not None:
            dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
            # all datetime objs from openHAB have a timezone set so we can't easily compare them
            # --> TypeError: can't compare offset-naive and offset-aware datetime
            dt = dt.astimezone(tz=None)   # Changes datetime object so it uses system timezone
            value = dt.replace(tzinfo=None)  # Removes timezone awareness
        return cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)
