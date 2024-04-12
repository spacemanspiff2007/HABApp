from typing import List

from pytest import MonkeyPatch

import HABApp
import HABApp.core.lib.exceptions.format
import HABApp.rule.rule as rule_module
import HABApp.rule.scheduler.habappschedulerview as ha_sched
from HABApp.core.asyncio import async_context
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

    def __init__(self):
        SyncScheduler.ALL.append(self)
        self.jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    def remove_job(self, job):
        self.jobs.remove(job)

    def cancel_all(self):
        self.jobs.clear()


class DummyRuntime(Runtime):
    def __init__(self):
        pass


def raising_fallback_format(e: Exception, existing_traceback: List[str]) -> List[str]:
    traceback = fallback_format(e, existing_traceback)
    traceback = traceback
    raise


class SimpleRuleRunner:
    def __init__(self):
        self.loaded_rules = []

        self.monkeypatch = MonkeyPatch()
        self.restore = []

    def submit(self, callback, *args, **kwargs):
        # This executes the callback so we can not ignore exceptions
        callback(*args, **kwargs)

    def set_up(self):
        # ensure that we call setup only once!
        assert isinstance(HABApp.core.Items, ConstProxyObj)
        assert isinstance(HABApp.core.EventBus, ConstProxyObj)

        ir = ItemRegistry()
        eb = EventBus()
        self.restore = setup_internals(ir, eb, final=False)

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
        self.monkeypatch.setattr(ha_sched, '_HABAppScheduler', SyncScheduler)

    def tear_down(self):
        ctx = async_context.set('Tear down test')

        for rule in self.loaded_rules:
            rule._habapp_ctx.unload_rule()
        self.loaded_rules.clear()

        # restore patched
        self.monkeypatch.undo()
        async_context.reset(ctx)

        for r in self.restore:
            r.restore()

    def process_events(self):
        for s in SyncScheduler.ALL:
            for job in s.jobs:
                job._func.execute()

    def __enter__(self):
        self.set_up()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tear_down()
        # do not supress exception
        return False
