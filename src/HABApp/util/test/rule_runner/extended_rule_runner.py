from typing import Optional

import eascheduler.jobs.job_base
import eascheduler.jobs.job_base_datetime
import eascheduler.jobs.job_countdown
import eascheduler.jobs.job_day_of_week
import eascheduler.jobs.job_reoccuring
import eascheduler.jobs.job_sun
import pendulum
from eascheduler.const import local_tz
from HABApp.core.items import base_item, base_valueitem
from HABApp.openhab.items import thing_item
from pendulum.datetime import DateTime
from pendulum.duration import Duration

from .rule_runner import SimpleRuleRunner, SyncScheduler


class TimeAwareRuleRunner(SimpleRuleRunner):
    def __init__(self, now: Optional[DateTime] = None):
        super().__init__()

        if now is not None:
            self.now = now
        else:
            self.now = pendulum.now()

    def set_up(self):
        super().set_up()

        def now(tz=None):
            if tz is not None:
                return self.now.in_tz(tz)
            else:
                return self.now

        # patch pendulum.now to simulate time
        self.monkeypatch.setattr(pendulum, "now", now)
        for mod in [
            eascheduler.jobs.job_base,
            eascheduler.jobs.job_base_datetime,
            eascheduler.jobs.job_countdown,
            eascheduler.jobs.job_day_of_week,
            eascheduler.jobs.job_reoccuring,
            eascheduler.jobs.job_sun,
        ]:
            self.monkeypatch.setattr(mod, "get_now", now)
        self.monkeypatch.setattr(base_item, "pd_now", now)
        self.monkeypatch.setattr(base_valueitem, "pd_now", now)
        self.monkeypatch.setattr(thing_item, "pd_now", now)

    def advance_time_by(self, duration: Duration, process_events: bool = True):
        self.now = self.now + duration
        if process_events:
            self.process_events()

    def advance_time_until(
        self,
        until: DateTime,
        step_size: Duration = pendulum.duration(seconds=1),
        process_events: bool = True,
    ):
        if until < self.now:
            raise ValueError(f"Cannot advance to an earlier date! {until}<{self.now}")
        while until > self.now:
            self.advance_time_by(duration=step_size, process_events=process_events)

    def process_events(self):
        for s in SyncScheduler.ALL:
            for job in s.jobs:
                if job.get_next_run() <= pendulum.now(local_tz).naive():
                    job._execute()
