import datetime
import typing

from pytz import utc

import HABApp
from HABApp.core.items.base_item import BaseItem


class OpenhabItem(BaseItem):
    """Openhab Item

    :ivar str ~.name: Name of the item (read only)
    :ivar ~.value: Value of the item, can be anything (read only)
    :ivar ~.datetime.datetime last_change: Timestamp of the last time when the item has changed the value (read only)
    :ivar ~.datetime.datetime last_update: Timestamp of the last time when the item has updated the value (read only)
    """

    def __init__(self, name: str, initial_value=None):
        super().__init__(name)

        self.value: typing.Any = initial_value

    def set_value(self, new_value) -> bool:
        """Set a new value without creating events on the event bus

        :param new_value: new value of the item
        :return: True if state has changed
        """
        state_changed = self.value != new_value

        _now = datetime.datetime.now(tz=utc)
        if state_changed:
            self._last_change = _now
        self._last_update = _now

        self.value = new_value
        return state_changed

    def post_value(self, new_value):
        """Set a new value and post appropriate events on the HABApp event bus
        (``ValueUpdateEvent``, ``ValueChangeEvent``)

        :param new_value: new value of the item
        """
        old_value = self.value
        self.set_value(new_value)

        # create events
        HABApp.core.EventBus.post_event(self._name, HABApp.core.events.ValueUpdateEvent(self._name, self.value))
        if old_value != self.value:
            HABApp.core.EventBus.post_event(
                self._name, HABApp.core.events.ValueChangeEvent(self._name, value=self.value, old_value=old_value)
            )
        return None

    def get_value(self, default_value=None) -> typing.Any:
        """Return the value of the item.

        :param default_value: Return this value if the item value is None
        :return: value of the item
        """
        if self.value is None:
            return default_value
        return self.value

    def __repr__(self):
        ret = ''
        for k in ['name', 'value', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    # only support == and != operators by default
    # __ne__ delegates to __eq__ and inverts the result so this is not overloaded separately
    def __eq__(self, other):
        return self.value == other

    def __bool__(self):
        return bool(self.value)

    # rich comparisons only for numeric types (int and float)
    def __lt__(self, other):
        if not isinstance(self.value, (int, float)):
            return NotImplemented
        return self.value < other

    def __le__(self, other):
        if not isinstance(self.value, (int, float)):
            return NotImplemented
        return self.value <= other

    def __ge__(self, other):
        if not isinstance(self.value, (int, float)):
            return NotImplemented
        return self.value >= other

    def __gt__(self, other):
        if not isinstance(self.value, (int, float)):
            return NotImplemented
        return self.value > other
