from __future__ import annotations

import inspect

import eascheduler.scheduler_view
from HABApp.core.internals import uses_item_registry
from HABApp.core.items import BaseValueItem
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.items import OpenhabItem
from eascheduler.const import FAR_FUTURE
from eascheduler.jobs import (
    CountdownJob as CountdownJobBase, DawnJob as DawnJobBase, DayOfWeekJob as DayOfWeekJobBase,
    DuskJob as DuskJobBase, OneTimeJob as OneTimeJobBase, ReoccurringJob as ReoccurringJobBase,
    SunriseJob as SunriseJobBase, SunsetJob as SunsetJobBase
)
from eascheduler.jobs.job_base import ScheduledJobBase

Items = uses_item_registry()


class ItemBoundJobMixin:
    def __init__(self):
        super().__init__()
        self._item: BaseValueItem | None = None

    @ignore_exception
    def _timestamp_to_item(self, job: ScheduledJobBase):
        if self._item is None:
            return None

        if self._next_run >= FAR_FUTURE:
            next_run = None
        else:
            next_run = self.get_next_run()

        if isinstance(self._item, OpenhabItem):
            self._item.oh_post_update(next_run)
        else:
            self._item.post_value(next_run)

        # if the job has been canceled we clean this up, too
        if self._parent is None:
            self._item = None
            self._next_run_callback = None

    def to_item(self, item: str | BaseValueItem | None):
        """Sends the next execution (date)time to an item. Sends ``None`` if the job is not scheduled.

        :param item: item name or item, None to disable
        """
        if item is None:
            self._item = None
            self._next_run_callback = None
        else:
            self._item = Items.get_item(item) if not isinstance(item, BaseValueItem) else item
            self._next_run_callback = self._timestamp_to_item
            # Update the item with the current timestamp
            self._timestamp_to_item(self)

    # I am not sure about this operator - it seems like a nice idea but doesn't work well
    # with the code inspections from the IDE
    #
    # def __gt__(self, other):
    #     if isinstance(other, (str, BaseValueItem, None)):
    #         self.to_item(other)
    #         return self
    #     return NotImplemented


class CountdownJob(CountdownJobBase, ItemBoundJobMixin):
    pass


class DawnJob(DawnJobBase, ItemBoundJobMixin):
    pass


class DayOfWeekJob(DayOfWeekJobBase, ItemBoundJobMixin):
    pass


class DuskJob(DuskJobBase, ItemBoundJobMixin):
    pass


class OneTimeJob(OneTimeJobBase, ItemBoundJobMixin):
    pass


class ReoccurringJob(ReoccurringJobBase, ItemBoundJobMixin):
    pass


class SunriseJob(SunriseJobBase, ItemBoundJobMixin):
    pass


class SunsetJob(SunsetJobBase, ItemBoundJobMixin):
    pass


# This is a very dirty hack - I really should come up with something different
def replace_jobs():
    g = globals()
    module = eascheduler.scheduler_view
    for name, obj in inspect.getmembers(module):
        if not name.endswith('Job'):
            continue

        assert obj is g[name + 'Base']
        setattr(module, name, g[name])


replace_jobs()
