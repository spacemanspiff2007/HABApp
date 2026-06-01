from __future__ import annotations

from asyncio import CancelledError, Task, create_task, sleep
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Final, Self

from whenever import Instant, TimeDelta

from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine


@HABAPP_PROVIDER.register
class DebouncedCallRegistry:
    __slots__ = ('_objs', '_tasks', 'enabled')

    def __init__(self) -> None:
        self._tasks: Final[set[Task]] = set()
        self._objs: tuple[DebouncedCallBase, ...] = ()

        self.enabled: bool = True

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} tasks={len(self._tasks)} objs={len(self._objs)}>'

    def __contains__(self, item: DebouncedCallBase) -> bool:
        return item in self._objs

    def register_obj(self, obj: DebouncedCallBase) -> Self:
        if obj not in self._objs:
            self._objs += (obj, )
        return self

    def remove_obj(self, obj: DebouncedCallBase) -> Self:
        self._objs = tuple(o for o in self._objs if o is not obj)
        return self

    async def sleep_until(self, target: Instant) -> None:
        delay: Final[float] = (target - Instant.now()).in_seconds()
        await sleep(delay)

    def create_task[T](self, coro: Coroutine[Any, Any, T]) -> Task[T]:
        task: Final = create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def shutdown(self) -> None:
        self.enabled = False

        for obj in self._objs:
            obj.cancel()

        # wait till tasks are done
        while self._tasks:
            try:  # noqa: SIM105
                await next(iter(self._tasks))
            except CancelledError:
                pass


class DebouncedCallBase:
    __slots__ = ('_due_at', '_registry', '_task', '_timeout')

    def __init__(self, timeout: float | TimeDelta, registry: DebouncedCallRegistry) -> None:
        self._timeout: TimeDelta = self._get_timeout(timeout)
        self._registry: Final[DebouncedCallRegistry] = registry.register_obj(self)
        self._task: Task | None = None
        self._due_at: Instant  = Instant.now()

    def __repr__(self) -> str:
        additional_text: str = self._repr_parts()
        return (f'<{self.__class__.__name__}{additional_text:s} timeout={self._timeout} '
                f'running={self._task is not None}>')

    def _repr_parts(self) -> str:
        return ''

    @staticmethod
    def _get_timeout(timeout: float | TimeDelta) -> TimeDelta:
        if isinstance(timeout, (int, float)):
            timeout = TimeDelta(seconds=timeout)

        if not isinstance(timeout, TimeDelta):
            msg = f'Timeout must be a TimeDelta or int/float, is {type(timeout)}'
            raise TypeError(msg)

        if timeout < TimeDelta.ZERO:
            msg = f'Timeout must be a >= 0! Is: {timeout}'
            raise ValueError(msg)
        return timeout

    def cancel(self) -> None:
        if (t := self._task) is None:
            return None
        self._task = None

        # only cancel if it is not run or canceled
        if not (t.done() or t.cancelled()):
            t.cancel()
        return None

    def reset(self) -> None:
        self._due_at = Instant.now() + self._timeout
        self.cancel()

        if not self._registry.enabled:
            return None

        self._task = task = self._registry.create_task(self._countdown_task())
        task.add_done_callback(self._task_done)
        return None

    def _task_done(self, task: Task) -> None:
        if task is self._task:
            self._task = None

    async def _countdown_task(self) -> None:
        reg: Final = self._registry

        await reg.sleep_until(self._due_at)

        # the run logic should always be executed completely,
        # that's why we shield it from cancellation by running it as a new task
        reg.create_task(self._run())

    async def _run(self) -> None:
        raise NotImplementedError()


class DebouncedCall(DebouncedCallBase):
    __slots__ = ('_func', )

    def __init__(self, func: Callable[[], Awaitable[Any]],
                 timeout: float | TimeDelta, registry: DebouncedCallRegistry) -> None:
        super().__init__(timeout, registry)

        # coro-func or a class that implements __call__ that is a coro-func
        if not (iscoroutinefunction(func) or iscoroutinefunction(getattr(func, '__call__', None))):  # noqa: B004
            msg = f'Function must be a coroutine function or callable returning an awaitable, is {type(func)}'
            raise TypeError(msg)

        self._func: Final[Callable[[], Awaitable[Any]]] = func

    def _repr_parts(self) -> str:
        return f' func={self._func.__name__:s}'

    async def _run(self) -> None:
        await self._func()
