from datetime import datetime
from typing import TYPE_CHECKING, Optional, FrozenSet, Mapping

from HABApp.core.const.const import PYTHON_311
from HABApp.openhab.items.base_item import OpenhabItem, MetaData

if TYPE_CHECKING:
    Optional = Optional
    FrozenSet = FrozenSet
    Mapping = Mapping
    MetaData = MetaData


class DatetimeItem(OpenhabItem):
    """DateTimeItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar datetime value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        # see implementation im map_values.py
        if PYTHON_311:
            dt = datetime.fromisoformat(state)
        else:
            pos_dot = state.find('.')
            pos_plus = state.find('+')
            if pos_plus - pos_dot > 6:
                state = state[:pos_dot + 7] + state[pos_plus:]
            dt = datetime.strptime(state, '%Y-%m-%dT%H:%M:%S.%f%z')

        # all datetime objs from openHAB have a timezone set so we can't easily compare them
        # --> TypeError: can't compare offset-naive and offset-aware datetime
        dt = dt.astimezone(tz=None)  # Changes datetime object so it uses system timezone
        value = dt.replace(tzinfo=None)  # Removes timezone awareness
        return value
