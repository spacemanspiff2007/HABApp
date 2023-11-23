from typing import Optional, Type, TypeVar

from eascheduler.const import local_tz
from pendulum import UTC, DateTime
from pendulum import now as pd_now

from HABApp.core.internals import (
    HINT_EVENT_BUS_LISTENER,
    HINT_EVENT_FILTER_OBJ,
    get_current_context,
    uses_get_item,
    uses_item_registry,
)
from HABApp.core.internals.item_registry import ItemRegistryItem
from HABApp.core.lib.parameters import TH_POSITIVE_TIME_DIFF, get_positive_time_diff

from ..const.hints import TYPE_EVENT_CALLBACK
from .base_item_times import ChangedTime, ItemNoChangeWatch, ItemNoUpdateWatch, UpdatedTime
from .tmp_data import add_tmp_data as _add_tmp_data
from .tmp_data import restore_tmp_data as _restore_tmp_data


get_item = uses_get_item()
item_registry = uses_item_registry()


class BaseItem(ItemRegistryItem):
    """BaseItem, all items must inherit from this class
    """

    @classmethod
    def get_item(cls, name: str):
        """Returns an already existing item. If it does not exist or has a different item type an exception will occur.

        :param name: Name of the item
        """
        assert isinstance(name, str), type(name)
        item = get_item(name)
        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def __init__(self, name: str):
        super().__init__(name)

        _now = pd_now(UTC)
        self._last_change: ChangedTime = ChangedTime(self._name, _now)
        self._last_update: UpdatedTime = UpdatedTime(self._name, _now)

    @property
    def last_change(self) -> DateTime:
        """
        :return: Timestamp of the last time when the item has been changed (read only)
        """
        return self._last_change.dt.in_timezone(local_tz).naive()

    @property
    def last_update(self) -> DateTime:
        """
        :return: Timestamp of the last time when the item has been updated (read only)
        """
        return self._last_update.dt.in_timezone(local_tz).naive()

    def __repr__(self):
        ret = ''
        for k in ['name', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    def watch_change(self, secs: TH_POSITIVE_TIME_DIFF) -> ItemNoChangeWatch:
        """Generate an event if the item does not change for a certain period of time.
        Has to be called from inside a rule function.

        :param secs: secs after which the event will occur, max 1 decimal digit for floats
        :return: The watch obj which can be used to cancel the watch
        """
        secs = get_positive_time_diff(secs, round_digits=1)
        return self._last_change.add_watch(secs)

    def watch_update(self, secs: TH_POSITIVE_TIME_DIFF) -> ItemNoUpdateWatch:
        """Generate an event if the item does not receive and update for a certain period of time.
        Has to be called from inside a rule function.

        :param secs: secs after which the event will occur, max 1 decimal digit for floats
        :return: The watch obj which can be used to cancel the watch
        """
        secs = get_positive_time_diff(secs, round_digits=1)
        return self._last_update.add_watch(secs)

    def listen_event(self, callback: TYPE_EVENT_CALLBACK,
                     event_filter: Optional[HINT_EVENT_FILTER_OBJ] = None) -> HINT_EVENT_BUS_LISTENER:
        """
        Register an event listener which listens to all event that the item receives

        :param callback: callback that accepts one parameter which will contain the event
        :param event_filter: Event filter. This is typically :class:`~HABApp.core.events.ValueUpdateEventFilter` or
            :class:`~HABApp.core.events.ValueChangeEventFilter` which will also trigger on changes/update from openhab
            or mqtt. Additionally it can be an instance of :class:`~HABApp.core.events.EventFilter` which additionally
            filters on the values of the event. It is also possible to group filters logically with, e.g.
            :class:`~HABApp.core.events.AndFilterGroup` and :class:`~HABApp.core.events.OrFilterGroup`
        """
        return get_current_context().rule.listen_event(self._name, callback=callback, event_filter=event_filter)

    def _on_item_added(self):
        """This function gets automatically called when the item is added to the item registry
        """
        _restore_tmp_data(self)

    def _on_item_removed(self):
        """This function gets automatically called when the item is removed from the item registry
        """
        _add_tmp_data(self)


# Hints for functions that use an item class as an input parameter
HINT_ITEM_OBJ = TypeVar('HINT_ITEM_OBJ', bound=BaseItem)
HINT_TYPE_ITEM_OBJ = Type[HINT_ITEM_OBJ]
