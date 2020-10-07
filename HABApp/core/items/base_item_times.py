import asyncio
import datetime
import typing

from HABApp.core.wrapper import log_exception
from .base_item_watch import BaseWatch, ItemNoChangeWatch, ItemNoUpdateWatch
from ..const import loop


class ItemTimes:
    WATCH: typing.Union[typing.Type[ItemNoUpdateWatch], typing.Type[ItemNoChangeWatch]]

    def __init__(self, name: str, dt: datetime.datetime):
        self.name: str = name
        self.dt: datetime.datetime = dt
        self.tasks: typing.List[BaseWatch] = []

    def set(self, dt: datetime.datetime, events=True):
        self.dt = dt
        if not self.tasks:
            return

        if events:
            asyncio.run_coroutine_threadsafe(self.schedule_events(), loop)
        return None

    def add_watch(self, secs: typing.Union[int, float]) -> BaseWatch:
        assert secs > 0, secs

        # don't add the watch two times
        for t in self.tasks:
            if not t._fut.is_canceled and t._fut.secs == secs:
                return t
        w = self.WATCH(self.name, secs)
        self.tasks.append(w)
        return w

    @log_exception
    async def schedule_events(self):
        clean = False
        for t in self.tasks:
            if t._fut.is_canceled:
                clean = True
            else:
                t._fut.reset()

        # remove canceled tasks
        if clean:
            self.tasks = [t for t in self.tasks if not t._fut.is_canceled]
        return None


class UpdatedTime(ItemTimes):
    WATCH = ItemNoUpdateWatch


class ChangedTime(ItemTimes):
    WATCH = ItemNoChangeWatch
