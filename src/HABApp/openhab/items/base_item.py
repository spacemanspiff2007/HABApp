import datetime
from typing import Any, FrozenSet, Mapping, NamedTuple, Optional, TypeVar, Type

from immutables import Map

from HABApp.core.const import MISSING
from HABApp.core.items import BaseValueItem
from HABApp.core.lib.funcs import compare as _compare
from HABApp.openhab.interface import get_persistence_data, post_update, send_command


class MetaData(NamedTuple):
    value: str
    config: Mapping[str, Any] = Map()


class OpenhabItem(BaseValueItem):
    """Base class for items which exists in OpenHAB.

    :ivar str name:
    :ivar Any value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    def __init__(self, name: str, initial_value=None,
                 label: Optional[str] = None, tags: FrozenSet[str] = frozenset(), groups: FrozenSet[str] = frozenset(),
                 metadata: Mapping[str, MetaData] = Map()):
        super().__init__(name, initial_value)
        self.label: Optional[str] = label
        self.tags: FrozenSet[str] = tags
        self.groups: FrozenSet[str] = groups
        self.metadata: Mapping[str, MetaData] = metadata

    @classmethod
    def from_oh(cls, name: str, value=None,
                label: Optional[str] = None, tags: FrozenSet[str] = frozenset(), groups: FrozenSet[str] = frozenset(),
                metadata: Mapping[str, MetaData] = Map()):
        return cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)

    def oh_send_command(self, value: Any = MISSING):
        """Send a command to the openHAB item

        :param value: (optional) value to be sent. If not specified the current item value will be used.
        """
        send_command(self.name, self.value if value is MISSING else value)

    def oh_post_update(self, value: Any = MISSING):
        """Post an update to the openHAB item

        :param value: (optional) value to be posted. If not specified the current item value will be used.
        """
        post_update(self.name, self.value if value is MISSING else value)

    def oh_post_update_if(self, new_value, *, equal=MISSING, eq=MISSING, not_equal=MISSING, ne=MISSING,
                          lower_than=MISSING, lt=MISSING, lower_equal=MISSING, le=MISSING,
                          greater_than=MISSING, gt=MISSING, greater_equal=MISSING, ge=MISSING,
                          is_=MISSING, is_not=MISSING) -> bool:
        """
        Post a value depending on the current state of the item. If one of the comparisons is true the new state
        will be posted.

        :param new_value: new value to post
        :param equal: item state has to be equal to the passed value
        :param eq: item state has to be equal to the passed value
        :param not_equal: item state has to be not equal to the passed value
        :param ne: item state has to be not equal to the passed value
        :param lower_than: item state has to be lower than the passed value
        :param lt: item state has to be lower than the passed value
        :param lower_equal: item state has to be lower equal the passed value
        :param le: item state has to be lower equal the passed value
        :param greater_than: item state has to be greater than the passed value
        :param gt: item state has to be greater than the passed value
        :param greater_equal: item state has to be greater equal the passed value
        :param ge: tem state has to be greater equal the passed value
        :param is_: item state has to be the same object as the passt value (e.g. None)
        :param is_not: item state has to be not the same object as the passt value (e.g. None)

        :return: `True` if the new value was posted else `False`
        """

        if _compare(self.value, equal=equal, eq=eq, not_equal=not_equal, ne=ne,
                    lower_than=lower_than, lt=lt, lower_equal=lower_equal, le=le,
                    greater_than=greater_than, gt=gt, greater_equal=greater_equal, ge=ge, is_=is_, is_not=is_not):
            post_update(self.name, new_value)
            return True
        return False

    def get_persistence_data(self, persistence: Optional[str] = None,
                             start_time: Optional[datetime.datetime] = None,
                             end_time: Optional[datetime.datetime] = None):
        """Query historical data from the OpenHAB persistence service

        :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
        :param start_time: return only items which are newer than this
        :param end_time: return only items which are older than this
        """

        return get_persistence_data(
            self.name, persistence, start_time, end_time
        )


HINT_OPENHAB_ITEM = TypeVar('HINT_OPENHAB_ITEM', bound=OpenhabItem)
HINT_TYPE_OPENHAB_ITEM = Type[HINT_OPENHAB_ITEM]
