import asyncio
import warnings
from asyncio import get_event_loop
from collections.abc import Awaitable
from types import TracebackType
from typing import Self
from unittest.mock import Mock

from astral import Observer
from eascheduler.producers import prod_sun as prod_sun_module
from pytest import MonkeyPatch  # noqa: PT013

import HABApp
import HABApp.core.lib.exceptions.format
import HABApp.rule.rule as rule_module
import HABApp.rule.scheduler.job_builder as job_builder_module
from HABApp.core.const.topics import TOPIC_ERRORS, TOPIC_WARNINGS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.files import FileManager
from HABApp.core.internals import EventBus, ItemRegistry, setup_internals
from HABApp.core.internals.event_bus import EventBusListenerBase
from HABApp.core.internals.function_executor.testing import TestingExecutorFactory
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.lib.asyncio import AsyncioProvider
from HABApp.core.lib.exceptions.format import fallback_format
from HABApp.mqtt import MqttAsyncInterface, MqttInterface
from HABApp.openhab.connection.handler import OpenHabAsyncInterface, OpenHabSyncInterface
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


class AppendListener(EventBusListenerBase):
    def __init__(self, topic: str, obj: list) -> None:
        super().__init__(topic)
        self.obj = obj

    def notify_listeners(self, event) -> None:
        self.obj.append(event)

    def describe(self) -> str:
        return f'AppendListener({self.topic})'


class ErrorEventReceivedError(Exception):
    pass


class WarningReceivedError(Exception):
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

        self._code_warnings = []

        self._ignored_exceptions: tuple[Exception, ...] = ignored_exceptions

    def add_warning(self, message, category, filename, lineno, file=None, line=None) -> None:
        self._code_warnings.append(f'{filename}:{lineno}: {category.__name__}:{message}')

    def set_ignored_exceptions(self, *exceptions: type[Exception]) -> None:
        self._ignored_exceptions = exceptions

    async def set_up(self) -> None:
        # ensure that we call setup only once!
        assert isinstance(HABApp.core.Items, ConstProxyObj)
        assert isinstance(HABApp.core.EventBus, ConstProxyObj)

        ir = ItemRegistry()
        eb = EventBus()
        async_provider = AsyncioProvider()
        file_manager = FileManager(None, eb, async_provider)
        self.restore = setup_internals(ir, eb, final=False)

        # setup so we capture errors / warnings
        eb.add_listener(AppendListener(TOPIC_WARNINGS, self._warnings))
        eb.add_listener(AppendListener(TOPIC_ERRORS, self._errors))

        # Scheduler
        self.monkeypatch.setattr(prod_sun_module, 'OBSERVER', Observer(52.51870523376821, 13.376072914752532, 10))

        # Overwrite
        self.monkeypatch.setattr(HABApp.core, 'EventBus', eb)
        self.monkeypatch.setattr(HABApp.core, 'Items', ir)

        # Patch the hook so we can instantiate the rules
        hook = HABAppRuleHook(
            self.loaded_rules.append, suggest_rule_name, DummyRuntime(), None, get_event_loop(), None,
            item_registry=ir, event_bus=eb, executor_factory=TestingExecutorFactory(eb),
            oh_interface_sync=Mock(OpenHabSyncInterface), oh_interface_async=Mock(OpenHabAsyncInterface),
            mqtt_interface_sync=Mock(MqttInterface), mqtt_interface_async=Mock(MqttAsyncInterface),
        )
        self.monkeypatch.setattr(rule_module, '_get_rule_hook', lambda: hook)

        # raise exceptions during error formatting
        self.monkeypatch.setattr(HABApp.core.lib.exceptions.format, 'fallback_format', raising_fallback_format)

        # patch scheduler, so we run synchronous
        self.monkeypatch.setattr(job_builder_module, 'AsyncHABAppScheduler', SyncScheduler)

        # catch warnings
        self.monkeypatch.setattr(warnings, 'showwarning', self.add_warning)

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
                    lines.append(f'Error: {type(obj)}')
                    lines.extend(obj.splitlines())

                lines.append(f'Unknown error type: {type(obj)}')
                lines.extend(str(obj).splitlines())
                continue

            if lines:
                lines.insert(0, 'Error during test!')
                msg = '\n'.join(lines)
                raise ErrorEventReceivedError(msg)

        if self._code_warnings:
            lines = ['Code warnings:']
            lines.extend(self._code_warnings)
            msg = '\n'.join(lines)
            raise WarningReceivedError(msg)

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

        asyncio.run(_run())
