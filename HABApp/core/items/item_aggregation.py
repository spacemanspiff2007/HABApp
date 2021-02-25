import asyncio
import collections
import time
import typing
from datetime import timedelta

import HABApp
from . import BaseValueItem
from ..wrapper import process_exception


class AggregationItem(BaseValueItem):

    @classmethod
    def get_create_item(cls, name: str):
        """Creates a new AggregationItem in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :return: item
        """
        assert isinstance(name, str), type(name)

        try:
            item = HABApp.core.Items.get_item(name)
        except HABApp.core.Items.ItemNotFoundException:
            item = cls(name)
            HABApp.core.Items.add_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def __init__(self, name: str):
        super().__init__(name)
        self.__period: float = 0
        self.__aggregation_func: typing.Callable[[typing.Iterable], typing.Any] = lambda x: x

        self._ts: typing.Deque[float] = collections.deque()
        self._vals: typing.Deque[typing.Any] = collections.deque()

        self.__listener: typing.Optional[HABApp.core.EventBusListener] = None

        self.__task: typing.Optional[asyncio.Future] = None

    def aggregation_func(self, func: typing.Callable[[typing.Iterable], typing.Any]) -> 'AggregationItem':
        """Set the function which will be used to aggregate all values. E.g. ``min`` or ``max``

        :param func: The function which takes an iterator an returns an aggregated value.
                     Important: the function must be **non blocking**!
        """
        self.__aggregation_func = func
        return self

    def aggregation_period(self, period: typing.Union[float, int, timedelta]) -> 'AggregationItem':
        """Set the period in which the items will be aggregated

        :param period: period in seconds
        """
        if isinstance(period, timedelta):
            period = period.total_seconds()

        assert period > 0, period
        self.__period = period

        # Clean old items (e.g. if we made the period shorter)
        while len(self._ts) > 1 and self._ts[1] + self.__period < time.time():
            self._ts.popleft()
            self._vals.popleft()

        return self

    def aggregation_source(self, source: typing.Union[BaseValueItem, str],
                           only_changes: bool = False) -> 'AggregationItem':
        """Set the source item which changes will be aggregated

        :param source: name or Item obj
        :param only_changes: if true only value changes instead of value updates will be added
        """

        # If we already have one we cancel it
        if self.__listener is not None:
            self.__listener.cancel()
            self.__listener = None

        self.__listener = HABApp.core.EventBusListener(
            topic=source.name if isinstance(source, HABApp.core.items.BaseValueItem) else source,
            callback=HABApp.core.WrappedFunction(self._add_value, name=f'{self.name}.add_value'),
            event_type=HABApp.core.events.ValueChangeEvent if only_changes else HABApp.core.events.ValueUpdateEvent
        )
        HABApp.core.EventBus.add_listener(self.__listener)
        return self

    def _on_item_remove(self):
        super()._on_item_remove()

        if self.__listener is not None:
            self.__listener.cancel()
            self.__listener = None

        if self.__task is not None:
            self.__task.cancel()
            self.__task = None

    async def __update_task(self):
        try:
            while len(self._ts) > 1:
                ts = self._ts[1]
                now = time.time()

                left = (ts + self.__period) - now
                while left > 0:
                    await asyncio.sleep(left)
                    # sometimes we wake up to early
                    now = time.time()
                    left = (ts + self.__period) - now

                self._ts.popleft()
                self._vals.popleft()

                # old entries are removed -> now do the aggregation
                try:
                    val = self.__aggregation_func(self._vals)
                except Exception as e:
                    process_exception(self.__aggregation_func, e)
                    continue
                self.post_value(val)

        except Exception as e:
            process_exception(self.__update_task, e)
        finally:
            self.__task = None
        return None

    async def _add_value(self, event: 'HABApp.core.events.ValueChangeEvent'):
        self._ts.append(time.time())
        self._vals.append(event.value)

        if self.__task is None:
            # todo: rename to asyncio.create_task once we go py3.7 only
            self.__task = asyncio.ensure_future(self.__update_task())

        try:
            val = self.__aggregation_func(self._vals)
        except Exception as e:
            process_exception(self.__aggregation_func, e)
            return None

        self.post_value(val)
        return None
