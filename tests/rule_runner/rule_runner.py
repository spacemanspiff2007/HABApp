from types import TracebackType

from astral import Observer
from eascheduler.producers import prod_sun as prod_sun_module
from pytest import MonkeyPatch

import HABApp
import HABApp.core.lib.exceptions.format
import HABApp.rule.rule as rule_module
import HABApp.rule.scheduler.job_builder as job_builder_module
from HABApp.core.internals import EventBus, ItemRegistry, setup_internals
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.internals.wrapped_function import wrapped_thread, wrapper
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
    traceback = traceback
    raise


class SimpleRuleRunner:
    def __init__(self) -> None:
        self.loaded_rules = []

        self.monkeypatch = MonkeyPatch()
        self.restore = []

    def submit(self, callback, *args, **kwargs) -> None:
        # This executes the callback so we can not ignore exceptions
        callback(*args, **kwargs)

    def set_up(self) -> None:
        # ensure that we call setup only once!
        assert isinstance(HABApp.core.Items, ConstProxyObj)
        assert isinstance(HABApp.core.EventBus, ConstProxyObj)

        ir = ItemRegistry()
        eb = EventBus()
        self.restore = setup_internals(ir, eb, final=False)

        # Scheduler
        self.monkeypatch.setattr(prod_sun_module, 'OBSERVER', Observer(52.51870523376821, 13.376072914752532, 10))

        # Overwrite
        self.monkeypatch.setattr(HABApp.core, 'EventBus', eb)
        self.monkeypatch.setattr(HABApp.core, 'Items', ir)

        # Patch the hook so we can instantiate the rules
        hook = HABAppRuleHook(self.loaded_rules.append, suggest_rule_name, DummyRuntime(), None)
        self.monkeypatch.setattr(rule_module, '_get_rule_hook', lambda: hook)

        # patch worker with a synchronous worker
        self.monkeypatch.setattr(wrapped_thread, 'POOL', self)
        self.monkeypatch.setattr(wrapper, 'SYNC_CLS', WrappedThreadFunction, raising=False)

        # raise exceptions during error formatting
        self.monkeypatch.setattr(HABApp.core.lib.exceptions.format, 'fallback_format', raising_fallback_format)

        # patch scheduler, so we run synchronous
        self.monkeypatch.setattr(job_builder_module, 'AsyncHABAppScheduler', SyncScheduler)

    def tear_down(self) -> None:
        self.loaded_rules.clear()

        # restore patched
        self.monkeypatch.undo()

        for r in self.restore:
            r.restore()

    def process_events(self) -> None:
        for s in SyncScheduler.ALL:
            for job in s.jobs:
                job.executor.execute()

    def __enter__(self) -> None:
        self.set_up()

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        self.tear_down()
        # do not supress exception
        return False
