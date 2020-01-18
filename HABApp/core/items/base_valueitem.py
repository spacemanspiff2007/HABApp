import datetime
import typing
import logging

from pytz import utc

import HABApp
from .base_item import BaseItem


log = logging.getLogger('HABApp')


class ExpireData:
    def __init__(self):
        self.listener: typing.Optional[HABApp.core.EventBusListener] = None
        self.watcher: typing.Optional[HABApp.core.items.base_item.BaseWatch] = None

        self.value: typing.Any = None
        self.secs: int = -1

    def cancel(self):
        self.watcher.cancel()
        self.listener.cancel()
        self.value = None

    def create(self, watcher, listener, secs: int, default_value: typing.Any):
        assert isinstance(listener, HABApp.core.EventBusListener), type(watcher)
        assert isinstance(watcher, HABApp.core.items.base_item.BaseWatch), type(watcher)

        # Watcher and default value
        self.secs = secs
        self.value = default_value

        self.watcher = watcher
        self.listener = listener

        # We have to add the listener to the event bus
        HABApp.core.EventBus.add_listener(self.listener)

    def is_event(self, event):
        assert isinstance(event, HABApp.core.events.ItemNoUpdateEvent), type(event)
        if event.seconds == self.secs:
            return True
        return False


class BaseValueItem(BaseItem):
    """Simple item

    :ivar str ~.name: Name of the item (read only)
    :ivar ~.value: Value of the item, can be anything (read only)
    :ivar ~.datetime.datetime last_change: Timestamp of the last time when the item has changed the value (read only)
    :ivar ~.datetime.datetime last_update: Timestamp of the last time when the item has updated the value (read only)
    """

    def __init__(self, name: str, initial_value=None):
        super().__init__(name)

        self.value: typing.Any = initial_value
        self._expire: typing.Optional[ExpireData] = None

    def set_value(self, new_value) -> bool:
        """Set a new value without creating events on the event bus

        :param new_value: new value of the item
        :return: True if state has changed
        """
        state_changed = self.value != new_value

        _now = datetime.datetime.now(tz=utc)
        if state_changed:
            self._last_change.set(_now)
        self._last_update.set(_now)

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

    async def __expire_event(self, event):
        # We have nothing set - we do nothing
        if self._expire is None:
            return None

        # Check that the expire seconds match
        if not self._expire.is_event(event):
            return None
        self._expire_item()

    def _expire_item(self):
        raise NotImplementedError()

    def expire(self, secs: typing.Optional[int], default_value=None):
        """Automatically set the item to the specified value if there is no value update during a certain time.

        :param secs: Secs after which the default value will be set, ``None`` to cancel
        :param default_value: Value the item will be set
        """
        # We cancel all existing expires
        if self._expire is not None:
            self._expire.cancel()
            self._expire = None
            log.debug(f'Removed expire from {self._name}')

        # We just want to cancel
        if secs is None:
            return None
        assert secs > 0, f'secs must be > 0 (is {secs})'

        # Func which calls the expire
        func = HABApp.core.wrappedfunction.WrappedFunction(self.__expire_event, name=f'Expire.{self.name}')

        # Add event listener so the value gets set
        listener = HABApp.core.EventBusListener(self.name, func, HABApp.core.events.ItemNoUpdateEvent)
        watcher = self._last_update.add_watch(secs)

        self._expire = ExpireData()
        self._expire.create(watcher=watcher, listener=listener, secs=secs, default_value=default_value)

        # We remove the expire if we unload the rule
        HABApp.rule.get_parent_rule().register_on_unload(lambda: self.expire(None))

        log.debug(f'Added expire ({secs}s) to {self._name}')
        return None

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
