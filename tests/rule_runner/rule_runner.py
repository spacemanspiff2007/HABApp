import logging
from collections.abc import Awaitable, Callable, Coroutine
from concurrent.futures import Future
from types import TracebackType
from typing import Any, Final

from astral import Observer
from eascheduler.producers import prod_sun as prod_sun_module
from pytest import MonkeyPatch
from typing_extensions import Self, override

import HABApp
import HABApp.core.lib.exceptions.format
import HABApp.rule.rule as rule_module
import HABApp.rule.scheduler.job_builder as job_builder_module
from HABApp.core.const.topics import TOPIC_ERRORS, TOPIC_WARNINGS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.files import FileManager
from HABApp.core.internals import Context, EventBus, ItemRegistry, setup_internals
from HABApp.core.internals.event_bus import EventBusBaseListener
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.internals.wrapped_function import wrapped_thread, wrapper
from HABApp.core.internals.wrapped_function.base import P, R, WrappedFunctionBase
from HABApp.core.internals.wrapped_function.wrapped_thread import WrappedThreadFunction
from HABApp.core.lib.exceptions.format import fallback_format
from HABApp.rule.rule_hook import HABAppRuleHook
from HABApp.runtime import Runtime


def suggest_rule_name(obj: object) -> str:
    return f'TestRule.{obj.__class__.__name__}'


class SyncScheduler:
    ALL = []

    def __init__(self, event_loop=None, enabled=True) -> None:
        SyncScheduler.ALL.append(self)
        self.jobs = []

    def add_job(self, job) -> None:
        self.jobs.append(job)

    def update_job(self, job) -> None:
        self.remove_job(job)
        self.add_job(job)

    def remove_job(self, job) -> None:
        if job in self.jobs:
            self.jobs.remove(job)

    def remove_all(self) -> None:
        self.jobs.clear()

    def set_enabled(self, enabled: bool) -> None:  # noqa: FBT001
        pass


class DummyRuntime(Runtime):
    def __init__(self) -> None:
        pass


def raising_fallback_format(e: Exception, existing_traceback: list[str]) -> list[str]:
    traceback = fallback_format(e, existing_traceback)
    _ = traceback
    raise


class SyncPool:
    def submit(self, callback, *args, **kwargs) -> Future:
        # This executes the callback so we can not ignore exceptions
        res = callback(*args, **kwargs)

        f = Future()
        f.set_result(res)
        return f


class AsyncFunc(WrappedFunctionBase):
    def __init__(self, coro: Callable[P, Coroutine[Any, Any, R]],
                 name: str | None = None,
                 logger: logging.Logger | None = None,
                 context: Context | None = None) -> None:

        super().__init__(name=name, func=coro, logger=logger, context=context)
        self.coro: Final = coro

    @override
    def run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        raise NotImplementedError()

    @override
    async def async_run(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        return await self.coro(*args, **kwargs)


class AppendListener(EventBusBaseListener):
    def __init__(self, topic: str, obj: list) -> None:
        super().__init__(topic)
        self.obj = obj

    def notify_listeners(self, event) -> None:
        self.obj.append(event)

    def describe(self) -> str:
        return f'AppendListener({self.topic})'


class ErrorEventReceivedError(Exception):
    pass


class SimpleRuleRunner:
    def __init__(self, ignored_exceptions: tuple[Exception, ...] = ()) -> None:

        if not isinstance(ignored_exceptions, tuple):
            msg = 'ignored_exceptions must be a tuple, got {type(ignored_exceptions)}'
            raise TypeError(msg)

        self.loaded_rules = []

        self.monkeypatch = MonkeyPatch()
        self.restore = []

        self._warnings = []
        self._errors = []

        self._ignored_exceptions: tuple[Exception, ...] = ignored_exceptions

    def set_ignored_exceptions(self, *exceptions: type[Exception]) -> None:
        self._ignored_exceptions = exceptions

    async def set_up(self) -> None:
        # ensure that we call setup only once!
        assert isinstance(HABApp.core.Items, ConstProxyObj)
        assert isinstance(HABApp.core.EventBus, ConstProxyObj)

        ir = ItemRegistry()
        eb = EventBus()
        file_manager = FileManager(None)
        self.restore = setup_internals(ir, eb, file_manager, final=False)

        # setup so we capture errors / warnings
        eb.add_listener(AppendListener(TOPIC_WARNINGS, self._warnings))
        eb.add_listener(AppendListener(TOPIC_ERRORS, self._errors))

        # Scheduler
        self.monkeypatch.setattr(prod_sun_module, 'OBSERVER', Observer(52.51870523376821, 13.376072914752532, 10))

        # Overwrite
        self.monkeypatch.setattr(HABApp.core, 'EventBus', eb)
        self.monkeypatch.setattr(HABApp.core, 'Items', ir)

        # Patch the hook so we can instantiate the rules
        hook = HABAppRuleHook(self.loaded_rules.append, suggest_rule_name, DummyRuntime(), None)
        self.monkeypatch.setattr(rule_module, '_get_rule_hook', lambda: hook)

        # patch worker with a synchronous worker
        self.monkeypatch.setattr(wrapped_thread, 'POOL', SyncPool())
        self.monkeypatch.setattr(wrapper, 'WrappedAsyncFunction', AsyncFunc)
        self.monkeypatch.setattr(wrapper, 'SYNC_CLS', WrappedThreadFunction, raising=False)

        # raise exceptions during error formatting
        self.monkeypatch.setattr(HABApp.core.lib.exceptions.format, 'fallback_format', raising_fallback_format)

        # patch scheduler, so we run synchronous
        self.monkeypatch.setattr(job_builder_module, 'AsyncHABAppScheduler', SyncScheduler)

    async def tear_down(self) -> None:
        for rule in self.loaded_rules:
            await rule._habapp_ctx.unload_rule()

        self.loaded_rules.clear()

        # restore patched
        self.monkeypatch.undo()

        for r in self.restore:
            r.restore()

        for msg in self._warnings:
            print(msg)

        # raise in case of errors
        if self._errors:
            lines = []
            for obj in self._errors:
                if isinstance(obj, HABAppException):
                    if (ign := self._ignored_exceptions) and isinstance(obj.exception, ign):
                        continue
                    lines.append(f'Error: {type(obj.exception)}')
                    lines.extend(obj.to_str().splitlines())
                elif isinstance(obj, str):
                    if (ign := self._ignored_exceptions) and isinstance(obj, ign):
                        continue
                    lines.append(f'Error: {type(obj.exception)}')
                    lines.extend(obj.to_str().splitlines())

                lines.append(f'Unknown error type: {type(obj)}')
                lines.extend(str(obj).splitlines())
                continue

            if lines:
                lines.insert(0, 'Error during test!')
                msg = '\n'.join(lines)
                raise ErrorEventReceivedError(msg)

    def process_events(self) -> None:
        for s in SyncScheduler.ALL:
            for job in s.jobs:
                job.executor.execute()

    async def __aenter__(self) -> Self:
        await self.set_up()
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> bool:
        await self.tear_down()
        # do not supress exception
        return False

    @classmethod
    def run(cls, coro: Awaitable, *,
            process_events: bool = True, ignored_exceptions: tuple[Exception, ...] = ()) -> None:

        async def _run() -> None:
            async with cls(ignored_exceptions=ignored_exceptions) as obj:
                await coro
                if process_events:
                    obj.process_events()

        HABApp.core.asyncio.loop.run_until_complete(_run())
