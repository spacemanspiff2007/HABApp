from __future__ import annotations

import inspect
import logging
from asyncio import AbstractEventLoop
from asyncio import Future as _Future
from asyncio import Task as _Task
from asyncio import get_event_loop as _get_event_loop
from asyncio import run_coroutine_threadsafe as _run_coroutine_threadsafe
from contextvars import ContextVar as _ContextVar
from threading import get_ident
from typing import TYPE_CHECKING, Final
from typing import Any as _Any

import HABApp
from HABApp.core.const.installation import PYTHON_INSTALLATION_PATHS
from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.lib.helper import get_obj_name


if TYPE_CHECKING:
    from collections.abc import Awaitable as _Awaitable
    from collections.abc import Callable as _Callable
    from collections.abc import Coroutine as _Coroutine


thread_context: Final[_ContextVar[str]] = _ContextVar[str]('thread_ctx')
thread_ident: Final = get_ident()

loop_context: Final[_ContextVar[AbstractEventLoop]] = _ContextVar('loop_ctx')


class AsyncContextError(Exception):
    def __init__(self, func: _Callable) -> None:
        super().__init__()
        self.func: _Callable = func

    def __str__(self) -> str:
        return f'Function "{get_obj_name(self.func)}" may not be called from an async context!'


def thread_error_msg() -> None:
    call_stack = []
    for frame in reversed(inspect.stack()):
        for name in PYTHON_INSTALLATION_PATHS:
            if frame.filename.startswith(name):
                break
        else:
            call_stack.append(frame)

    error_msg = [
        'Thread usage detected but no thread marker "@in_thread" was used!',
        'See https://habapp.readthedocs.io/en/latest/troubleshooting.html for more information.',
    ]

    if len(call_stack) > 1:
        error_msg.append('Call stack:')
    if call_stack:
        error_msg.extend(f'{frame.filename:s}:{frame.lineno:d} {frame.function:s}' for frame in call_stack)

    log = logging.getLogger('HABApp')
    for line in error_msg:
        log.error(line)

    # send event so user can receive notification
    HABApp.core.EventBus.post_event(TOPIC_ERRORS, '\n'.join(error_msg))


def _is_in_thread() -> bool:
    thread_ctx: bool = thread_context.get(None) is not None
    same_ident = get_ident() == thread_ident

    # both markers point to async
    if not thread_ctx and same_ident:
        return False

    # both markers point to thread
    if thread_ctx and not same_ident:
        return True

    # markers are in different states -> log error but assume thread
    thread_error_msg()
    return True


_tasks = set()


def create_task[T](coro: _Coroutine[_Any, _Any, T], name: str | None = None) -> _Future[T]:
    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
    if _is_in_thread():
        f = _run_coroutine_threadsafe(_async_execute_awaitable(coro), loop_context.get())
        _tasks.add(f)
        f.add_done_callback(_tasks.discard)
        return f

    t = _get_event_loop().create_task(coro, name=name)
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)
    return t


def create_task_from_async[T](coro: _Coroutine[_Any, _Any, T], name: str | None = None) -> _Task[T]:
    t = _get_event_loop().create_task(coro, name=name)
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)
    return t


def run_coro_from_thread[T](coro: _Coroutine[_Any, _Any, T], calling: _Callable) -> T:
    # This function call is blocking, so it can't be called in the async context
    if not _is_in_thread():
        raise AsyncContextError(calling)

    fut = _run_coroutine_threadsafe(_async_execute_awaitable(coro), loop_context.get())
    return fut.result()


def run_func_from_async[**P, T](func: _Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Runs a function from an async context"""

    # we already have an async context
    if not _is_in_thread():
        return func(*args, **kwargs)

    # we are in a thread, that's why we can wait (and block) for the future
    future = _run_coroutine_threadsafe(_async_execute_func(func, *args, **kwargs), loop_context.get())
    return future.result()


async def _async_execute_func[**P, T](func: _Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Helper coroutine to execute a function from the event loop"""

    ctx = thread_context.set(None)
    try:
        return func(*args, **kwargs)
    finally:
        thread_context.reset(ctx)


async def _async_execute_awaitable[T](awaitable: _Awaitable[T]) -> T:
    """Helper coroutine to execute a coroutine from the event loop and wait for the result"""

    ctx = thread_context.set(None)
    try:
        return await awaitable
    finally:
        thread_context.reset(ctx)
