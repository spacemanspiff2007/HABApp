import datetime
import typing
import warnings
import tzlocal
from pytz import utc

import HABApp


class Item:
    """Simple item

    :ivar str ~.name: Name of the item (read only)
    :ivar ~.value: Value of the item, can be anything (read only)
    :ivar ~.datetime.datetime last_change: Timestamp of the last time when the item has changed the value (read only)
    :ivar ~.datetime.datetime last_update: Timestamp of the last time when the item has updated the value (read only)
    """

    @classmethod
    def get_item(cls, name: str):
        """Returns an already existing item. If it does not exist or has a different item type an exception will occur.

        :param name: Name of the item
        :return: the item
        """
        item = HABApp.core.Items.get_item(name)
        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    @classmethod
    def get_create_item(cls, name: str, initial_value=None):
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :return: item
        """
        assert isinstance(name, str), type(name)

        try:
            item = HABApp.core.Items.get_item(name)
        except HABApp.core.Items.ItemNotFoundException:
            item = cls(name, initial_value)
            HABApp.core.Items.set_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def __init__(self, name: str, initial_value=None):
        super().__init__()
        assert isinstance(name, str), type(name)

        self.name: str = name
        self.value: typing.Any = initial_value

        _now = datetime.datetime.now(tz=utc)
        self._last_change: datetime.datetime = _now
        self._last_update: datetime.datetime = _now

    @property
    def last_change(self):
        return self._last_change.astimezone(tzlocal.get_localzone()).replace(tzinfo=None)

    @property
    def last_update(self):
        return self._last_update.astimezone(tzlocal.get_localzone()).replace(tzinfo=None)

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
        HABApp.core.EventBus.post_event(self.name, HABApp.core.events.ValueUpdateEvent(self.name, self.value))
        if old_value != self.value:
            HABApp.core.EventBus.post_event(
                self.name, HABApp.core.events.ValueChangeEvent(self.name, value=self.value, old_value=old_value)
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

    # ------------------------------------------------------------------------------------------------------------------
    # Deprecated functions. Created 30.09.2019, Keep this around for some time so this doesn't brake anything
    # ------------------------------------------------------------------------------------------------------------------
    @property
    def state(self):
        warnings.warn("'state' is deprecated, use 'value' instead", DeprecationWarning, 2)
        return self.value

    def set_state(self, new_state) -> bool:
        warnings.warn("'set_state' is deprecated, use 'set_value' instead", DeprecationWarning, 2)
        return self.set_value(new_state)

    def post_state(self, new_state):
        warnings.warn("'post_state' is deprecated, use 'post_value' instead", DeprecationWarning, 2)
        self.post_value(new_state)

    def get_state(self, default_value=None) -> typing.Any:
        warnings.warn("'get_state' is deprecated, use 'get_value' instead", DeprecationWarning, 2)
        return self.get_value(default_value)
