from asyncio import CancelledError, Task, get_event_loop
from collections.abc import Callable, Coroutine
from typing import Any, Final


_TASK_REFS = set()


class SingleTask:
    __slots__ = ('coro', 'name', 'task')

    def __init__(self, coro: Callable[[], Coroutine[Any, Any, Any]], name: str | None = None) -> None:
        if name is None:
            name = f'{self.__class__.__name__}_{coro.__name__}'

        self.coro: Final[Callable[[], Coroutine[Any, Any, Any]]] = coro
        self.name: Final[str] = name
        self.task: Task | None = None

    @property
    def is_running(self) -> bool:
        return self.task is not None and not self.task.done()

    def _set_task_none(self, task: Task) -> None:
        if self.task is task:
            self.task = None
        return None

    def cancel(self) -> Task | None:
        if (task := self.task) is None:
            return None

        self.task = None
        task.cancel()
        return task

    async def cancel_wait(self) -> None:
        if task := self.cancel():
            try:  # noqa: SIM105
                await task
            except CancelledError:
                pass

    async def wait(self) -> None:
        if self.task is None:
            return None

        try:  # noqa: SIM105
            await self.task
        except CancelledError:
            pass

    def start(self) -> Task:
        self.cancel()

        self.task = task = get_event_loop().create_task(self.coro(), name=self.name)
        task.add_done_callback(self._set_task_none)
        task.add_done_callback(_TASK_REFS.discard)
        return task

    def start_if_not_running(self) -> Task:
        if (t := self.task) is not None and not t.done():
            return t

        self.task = task = get_event_loop().create_task(self.coro(), name=self.name)
        task.add_done_callback(self._set_task_none)
        task.add_done_callback(_TASK_REFS.discard)
        return task
