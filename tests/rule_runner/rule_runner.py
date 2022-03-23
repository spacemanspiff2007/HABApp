from pytest import MonkeyPatch

import HABApp.rule.rule as rule_module
import HABApp.rule.scheduler.habappschedulerview as ha_sched
from HABApp.core.asyncio import async_context
from HABApp.core.internals.wrapped_function import wrapped_sync
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


class SimpleRuleRunner:
    def __init__(self):
        self.loaded_rules = []
        self.original_scheduler = None

        self.monkeypatch = MonkeyPatch()

    def restore(self):
        for obj, name, original in self._patched_objs:
            assert hasattr(obj, name)
            setattr(obj, name, original)

    def submit(self, callback, *args, **kwargs):
        # submit never raises and exception, so we don't do it here, too
        try:
            callback(*args, **kwargs)
        except Exception as e:  # noqa: F841
            pass

    def set_up(self):

        # Patch the hook so we can instantiate the rules
        hook = HABAppRuleHook(self.loaded_rules.append, suggest_rule_name, DummyRuntime(), None)
        self.monkeypatch.setattr(rule_module, '_get_rule_hook', lambda: hook)

        # patch worker with a synchronous worker
        self.monkeypatch.setattr(wrapped_sync, 'WORKERS', self)

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
