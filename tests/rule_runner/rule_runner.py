import sys

import HABApp.rule.scheduler.habappschedulerview as ha_sched
from HABApp.core import WrappedFunction
from HABApp.runtime import Runtime
from HABApp.core.context import async_context


def _get_topmost_globals() -> dict:
    depth = 1
    while True:
        try:
            var = sys._getframe(depth).f_globals    # noqa: F841
            depth += 1
        except ValueError:
            break
    return sys._getframe(depth - 1).f_globals


class TestRuleFile:
    def suggest_rule_name(self, obj):
        parts = str(type(obj)).split('.')
        return parts[-1][:-2]


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


class SimpleRuleRunner:
    def __init__(self):
        self.vars: dict = _get_topmost_globals()
        self.loaded_rules = []
        self.original_scheduler = None

        self._patched_objs = []

    def patch_obj(self, obj, name, new_value):
        assert hasattr(obj, name)
        self._patched_objs.append((obj, name, getattr(obj, name)))
        setattr(obj, name, new_value)

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
        self.vars['__UNITTEST__'] = True
        self.vars['__HABAPP__RUNTIME__'] = Runtime()
        self.vars['__HABAPP__RULE_FILE__'] = TestRuleFile()
        self.vars['__HABAPP__RULES'] = self.loaded_rules = []

        # patch worker with a synchronous worker
        self.patch_obj(WrappedFunction, '_WORKERS', self)

        # patch scheduler, so we run synchronous
        self.patch_obj(ha_sched, '_HABAppScheduler', SyncScheduler)


    def tear_down(self):
        async_context.set('Tear down test')

        self.vars.pop('__UNITTEST__')
        self.vars.pop('__HABAPP__RUNTIME__')
        self.vars.pop('__HABAPP__RULE_FILE__')
        loaded_rules = self.vars.pop('__HABAPP__RULES')
        for rule in loaded_rules:
            rule._unload()
        loaded_rules.clear()

        # restore patched
        self.restore()

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
