import datetime, typing

import tzlocal
from pytz import utc

import HABApp
from .item_times import ChangedTime, UpdatedTime


class BaseItem:

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
        return self._name

    @property
    def last_change(self) -> datetime.datetime:
        return self._last_change.dt.astimezone(tzlocal.get_localzone()).replace(tzinfo=None)

    @property
    def last_update(self) -> datetime.datetime:
        return self._last_update.dt.astimezone(tzlocal.get_localzone()).replace(tzinfo=None)

    def __repr__(self):
        ret = ''
        for k in ['name', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    def watch_change(self, secs: typing.Union[int, float]):
        """Generate an even if the item does not change for a certain period of time.
        Has to be called from a rule function.
        
        :param secs: secs after which the event will occur
        """
        if isinstance(secs, float):
            secs = round(secs, 1)
        else:
            assert isinstance(secs, int)
        w = self._last_change.add_watch(secs)
        HABApp.rule.get_parent_rule().register_cancel_obj(w)

    def watch_update(self, secs: typing.Union[int, float]):
        """Generate an even if the item does not receive and update for a certain period of time.
        Has to be called from a rule function.

        :param secs: secs after which the event will occur
        """
        if isinstance(secs, float):
            secs = round(secs, 1)
        else:
            assert isinstance(secs, int)
        w = self._last_update.add_watch(secs)
        HABApp.rule.get_parent_rule().register_cancel_obj(w)
