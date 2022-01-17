import logging
import typing
from datetime import timedelta
from typing import Generic, TypeVar, List

from pendulum import DateTime

from HABApp.core.context import create_task
from HABApp.core.wrapper import log_exception
from .base_item_watch import BaseWatch, ItemNoChangeWatch, ItemNoUpdateWatch

log = logging.getLogger('HABApp')

WATCH_TYPE = TypeVar("WATCH_TYPE", bound=BaseWatch)


class ItemTimes(Generic[WATCH_TYPE]):
    WATCH: typing.Union[typing.Type[ItemNoUpdateWatch], typing.Type[ItemNoChangeWatch]]

    def __init__(self, name: str, dt: DateTime):
        self.name: str = name
        self.dt: DateTime = dt
        self.tasks: List[WATCH_TYPE] = []

    def set(self, dt: DateTime, events=True):
        self.dt = dt
        if not self.tasks:
            return

        if events:
            create_task(self.schedule_events())
        return None

    def add_watch(self, secs: typing.Union[int, float, timedelta]) -> WATCH_TYPE:
        if isinstance(secs, timedelta):
            secs = secs.total_seconds()
        assert secs > 0, secs

        # don't add the watch two times
        for t in self.tasks:
            if not t.fut.is_canceled and t.fut.secs == secs:
                log.warning(f'Watcher {self.WATCH.__name__} ({t.fut.secs}s) for {self.name} has already been created')
                return t

        w = self.WATCH(self.name, secs)
        self.tasks.append(w)
        log.debug(f'Added {self.WATCH.__name__} ({w.fut.secs}s) for {self.name}')
        return w

    @log_exception
    async def schedule_events(self):
        canceled = []
        for t in self.tasks:
            if t.fut.is_canceled:
                canceled.append(t)
            else:
                t.fut.reset()

        # remove canceled tasks
        if canceled:
            for c in canceled:
                self.tasks.remove(c)
                log.debug(f'Removed {self.WATCH.__name__} ({c.fut.secs}s) for {self.name}')
        return None


class UpdatedTime(ItemTimes[ItemNoUpdateWatch]):
    WATCH = ItemNoUpdateWatch


class ChangedTime(ItemTimes[ItemNoChangeWatch]):
    WATCH = ItemNoChangeWatch
