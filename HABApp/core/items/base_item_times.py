import asyncio
import datetime
import typing

from HABApp.core.wrapper import log_exception
from .base_item_watch import BaseWatch, ItemNoUpdateWatch, ItemNoChangeWatch
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
            if t._secs == secs:
                return t
        w = self.WATCH(self.name, secs)
        self.tasks.append(w)
        return w

    @log_exception
    async def schedule_events(self):
        clean = False
        for t in self.tasks:
            if t._secs <= 0:
                clean = True
            else:
                # Schedule the new task, todo: rename to asyncio.create_task once we go py3.7 only
                asyncio.ensure_future(t._schedule_event())

        # remove canceled tasks
        if clean:
            self.tasks = [t for t in self.tasks if t._secs > 0]
        return None


class UpdatedTime(ItemTimes):
    WATCH = ItemNoUpdateWatch


class ChangedTime(ItemTimes):
    WATCH = ItemNoChangeWatch
