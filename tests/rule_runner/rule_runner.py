import sys

import HABApp.rule.habappscheduler as ha_sched
from HABApp.core import WrappedFunction
from HABApp.runtime import Runtime


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


class SimpleRuleRunner:
    def __init__(self):
        self.vars: dict = _get_topmost_globals()
        self.loaded_rules = []
        self.original_scheduler = None

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

        self.worker = WrappedFunction._WORKERS
        WrappedFunction._WORKERS = self

        # patch scheduler
        self.original_scheduler = ha_sched.ThreadSafeAsyncScheduler
        ha_sched.ThreadSafeAsyncScheduler = SyncScheduler

    def tear_down(self):
        self.vars.pop('__UNITTEST__')
        self.vars.pop('__HABAPP__RUNTIME__')
        self.vars.pop('__HABAPP__RULE_FILE__')
        loaded_rules = self.vars.pop('__HABAPP__RULES')
        for rule in loaded_rules:
            rule._unload()
        loaded_rules.clear()

        WrappedFunction._WORKERS = self.worker
        ha_sched.ThreadSafeAsyncScheduler = self.original_scheduler

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
