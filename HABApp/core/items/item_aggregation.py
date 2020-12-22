import asyncio
import collections
import time
import typing

import HABApp
from . import BaseValueItem
from ..wrapper import ignore_exception


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
        self.__aggregation_func: typing.Callable[[typing.Iterable], typing.Any] = lambda x: None

        self._ts: typing.Deque[float] = collections.deque()
        self._vals: typing.Deque[typing.Any] = collections.deque()

        self.__listener: typing.Optional[HABApp.core.EventBusListener] = None

    def aggregation_func(self, func: typing.Callable[[typing.Iterable], typing.Any]) -> 'AggregationItem':
        """Set the function which will be used to aggregate all values. E.g. ``min`` or ``max``

        :param func: The function which takes an iterator an returns an aggregated value.
                     Important: the function must be **non blocking**!
        """
        self.__aggregation_func = func
        return self

    def aggregation_period(self, period: typing.Union[float, int]) -> 'AggregationItem':
        """Set the period in which the items will be aggregated

        :param period: period in seconds
        """
        assert period > 0, period
        self.__period = period
        return self

    def aggregation_source(self, source: typing.Union[BaseValueItem, str]) -> 'AggregationItem':
        """Set the source item which changes will be aggregated

        :param item_or_name: name or Item obj
        """
        # If we already have one we cancel it
        if self.__listener is not None:
            self.__listener.cancel()
            self.__listener = None

        self.__listener = HABApp.core.EventBusListener(
            topic=source.name if isinstance(source, HABApp.core.items.BaseValueItem) else source,
            callback=HABApp.core.WrappedFunction(self._add_value, name=f'{self.name}.add_value'),
            event_type=HABApp.core.events.ValueChangeEvent
        )
        HABApp.core.EventBus.add_listener(self.__listener)
        return self

    def _on_item_remove(self):
        super()._on_item_remove()

        if self.__listener is not None:
            self.__listener.cancel()
            self.__listener = None

    async def __force_update(self):
        start = time.time()
        await asyncio.sleep(self.__period)
        sleep = time.time() - start

        # we need to sleep minimum the period, otherwise the value doesn't fall out of the interval
        # sometimes asyncio.sleep returns a little bit too early - this is what gets prevented here
        if sleep < self.__period:
            await asyncio.sleep(self.__period - sleep)

        self._aggregate()

    async def _add_value(self, event: 'HABApp.core.events.ValueChangeEvent'):
        self._ts.append(time.time())
        self._vals.append(event.value)

        # do another update when the value has fallen ouf of the period
        asyncio.ensure_future(self.__force_update())

        self._aggregate()
        return None

    @ignore_exception
    def _aggregate(self):
        # first remove entries which are too old
        now = time.time()
        while True:
            ct = len(self._ts)
            if ct <= 1:
                break

            # we keep one item from before the period because its value is valid into the period
            if (now - self._ts[1]) <= self.__period:
                break

            self._ts.popleft()
            self._vals.popleft()

        # old entries are removed -> now do the aggregation
        val = self.__aggregation_func(self._vals)
        self.post_value(val)
