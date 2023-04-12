import logging
from typing import Generic, TypeVar, List, Union, Type

from pendulum import DateTime

from HABApp.core.asyncio import run_func_from_async
from .base_item_watch import BaseWatch, ItemNoChangeWatch, ItemNoUpdateWatch

log = logging.getLogger('HABApp')

WATCH_OBJ = TypeVar("WATCH_OBJ", bound=BaseWatch)


class ItemTimes(Generic[WATCH_OBJ]):
    WATCH: Union[Type[ItemNoUpdateWatch], Type[ItemNoChangeWatch]]

    def __init__(self, name: str, dt: DateTime):
        self.name: str = name
        self.dt: DateTime = dt
        self.tasks: List[WATCH_OBJ] = []

    def set(self, dt: DateTime, events=True):
        self.dt = dt
        if not self.tasks:
            return

        if events:
            run_func_from_async(self.__async_schedule_events)
        return None

    def add_watch(self, secs: Union[int, float]) -> WATCH_OBJ:
        # don't add the watch two times
        for t in self.tasks:
            if not t.fut.is_canceled and t.fut.secs == secs:
                log.warning(f'Watcher {self.WATCH.__name__} ({t.fut.secs}s) for {self.name} has already been created')
                return t

        w = self.WATCH(self.name, secs)
        self.tasks.append(w)
        log.debug(f'Added {self.WATCH.__name__} ({w.fut.secs}s) for {self.name}')
        return w

    def __async_schedule_events(self):
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
