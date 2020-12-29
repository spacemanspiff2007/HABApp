import datetime
import typing

import tzlocal
from pytz import utc

import HABApp
from .base_item_times import ItemNoChangeWatch, ItemNoUpdateWatch, ChangedTime, UpdatedTime
from .tmp_data import add_tmp_data as _add_tmp_data
from .tmp_data import restore_tmp_data as _restore_tmp_data


class BaseItem:
    """BaseItem, all items must inherit from this class
    """

    @classmethod
    def get_item(cls, name: str):
        """Returns an already existing item. If it does not exist or has a different item type an exception will occur.

        :param name: Name of the item
        """
        assert isinstance(name, str), type(name)
        item = HABApp.core.Items.get_item(name)
        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def __init__(self, name: str):
        super().__init__()
        assert isinstance(name, str), type(name)

        self._name: str = name

        _now = datetime.datetime.now(tz=utc)
        self._last_change: ChangedTime = ChangedTime(self._name, _now)
        self._last_update: UpdatedTime = UpdatedTime(self._name, _now)

    @property
    def name(self) -> str:
        """
        :return: Name of the item (read only)
        """
        return self._name

    @property
    def last_change(self) -> datetime.datetime:
        """
        :return: Timestamp of the last time when the item has been changed (read only)
        """
        return self._last_change.dt.astimezone(tzlocal.get_localzone()).replace(tzinfo=None)

    @property
    def last_update(self) -> datetime.datetime:
        """
        :return: Timestamp of the last time when the item has been updated (read only)
        """
        return self._last_update.dt.astimezone(tzlocal.get_localzone()).replace(tzinfo=None)

    def __repr__(self):
        ret = ''
        for k in ['name', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    def watch_change(self, secs: typing.Union[int, float, datetime.timedelta]) -> ItemNoChangeWatch:
        """Generate an event if the item does not change for a certain period of time.
        Has to be called from inside a rule function.

        :param secs: secs after which the event will occur, max 1 decimal digit for floats
        :return: The watch obj which can be used to cancel the watch
        """
        if isinstance(secs, datetime.timedelta):
            secs = secs.total_seconds()
        if isinstance(secs, float):
            secs = round(secs, 1)
        else:
            assert isinstance(secs, int)
        assert secs > 0, secs
        w = self._last_change.add_watch(secs)
        HABApp.rule.get_parent_rule().register_cancel_obj(w)
        return w

    def watch_update(self, secs: typing.Union[int, float, datetime.timedelta]) -> ItemNoUpdateWatch:
        """Generate an event if the item does not receive and update for a certain period of time.
        Has to be called from inside a rule function.

        :param secs: secs after which the event will occur, max 1 decimal digit for floats
        :return: The watch obj which can be used to cancel the watch
        """
        if isinstance(secs, datetime.timedelta):
            secs = secs.total_seconds()
        if isinstance(secs, float):
            secs = round(secs, 1)
        else:
            assert isinstance(secs, int)
        assert secs > 0, secs
        w = self._last_update.add_watch(secs)
        HABApp.rule.get_parent_rule().register_cancel_obj(w)
        return w

    def listen_event(self, callback: typing.Callable[[typing.Any], typing.Any],
                     event_type: typing.Union['HABApp.core.events.AllEvents', typing.Any]
                     ) -> 'HABApp.core.EventBusListener':
        """
        Register an event listener which listens to all event that the item receives

        :param callback: callback that accepts one parameter which will contain the event
        :param event_type: Event filter. This is typically :class:`~HABApp.core.ValueUpdateEvent` or
            :class:`~HABApp.core.ValueChangeEvent` which will also trigger on changes/update from openHAB
            or mqtt.
        """
        rule = HABApp.rule.get_parent_rule()
        return rule.listen_event(self._name, callback=callback, event_type=event_type)

    def _on_item_add(self):
        """This function gets automatically called when the item is added to the item registry
        """
        _restore_tmp_data(self)

    def _on_item_remove(self):
        """This function gets automatically called when the item is removed from the item registry
        """
        _add_tmp_data(self)
