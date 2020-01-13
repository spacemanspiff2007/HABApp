import datetime

import tzlocal
from pytz import utc

import HABApp

local_tz = tzlocal.get_localzone()


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
        self._last_change: datetime.datetime = _now
        self._last_update: datetime.datetime = _now

    @property
    def name(self) -> str:
        return self._name

    @property
    def last_change(self) -> datetime.datetime:
        return self._last_change.astimezone(local_tz).replace(tzinfo=None)

    @property
    def last_update(self) -> datetime.datetime:
        return self._last_update.astimezone(local_tz).replace(tzinfo=None)

    def __repr__(self):
        ret = ''
        for k in ['name', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'
