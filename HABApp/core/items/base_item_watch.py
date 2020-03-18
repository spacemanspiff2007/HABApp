import asyncio
import typing

import HABApp
from ..const import loop
from ..events import ItemNoChangeEvent, ItemNoUpdateEvent


class BaseWatch:
    EVENT: typing.Union[typing.Type[ItemNoUpdateEvent], typing.Type[ItemNoChangeEvent]]

    def __init__(self, name: str, secs: typing.Union[int, float]):
        self._secs: typing.Union[int, float] = secs
        self._name: str = name
        self._task: typing.Optional[asyncio.Task] = None

    def __cancel_task(self):
        if self._task is None:
            return None

        if self._task.done() or self._task.cancelled():
            return None

        self._task.cancel()
        self._task = None

    async def _send_event(self):
        try:
            # wait time, during this time we can still cancel the task
            await asyncio.sleep(self._secs)
            # send event
            HABApp.core.EventBus.post_event(self._name, self.EVENT(self._name, self._secs))
        except asyncio.CancelledError:
            pass

    async def _schedule_event(self):
        self.__cancel_task()
        # Schedule the new tasks
        # todo: rename to asyncio.create_task once we go py3.7 only
        self._task = asyncio.ensure_future(self._send_event())

    async def __cancel_watch(self):
        self.__cancel_task()

    def cancel(self):
        """Cancel the item watch"""
        self._secs = 0  # we have to to set secs asap so we indicate that it is canceled
        asyncio.run_coroutine_threadsafe(self.__cancel_watch(), loop)


class ItemNoUpdateWatch(BaseWatch):
    EVENT = ItemNoUpdateEvent


class ItemNoChangeWatch(BaseWatch):
    EVENT = ItemNoChangeEvent
