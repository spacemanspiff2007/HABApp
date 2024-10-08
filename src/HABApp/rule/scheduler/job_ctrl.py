from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Final

from eascheduler.job_control.base import BaseControl
from typing_extensions import Self, override
from whenever import Instant

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.internals import uses_item_registry
from HABApp.core.items import BaseValueItem
from HABApp.openhab.items import OpenhabItem


if TYPE_CHECKING:
    from datetime import datetime as dt_datetime
    from datetime import timedelta as dt_timedelta

    from eascheduler.jobs import CountdownJob, DateTimeJob, OneTimeJob
    from eascheduler.jobs.base import JobBase


Items = uses_item_registry()


class HABAppBaseControl(BaseControl):
    def __init__(self) -> None:
        super().__init__()
        self._item: BaseValueItem | None = None

    def _cancel_timestamp_to_item(self, job: JobBase | None) -> None:
        self._timestamp_to_item(None)
        self._item = None
        self._job.on_update.remove(self._timestamp_to_item)
        self._job.on_finished.remove(self._cancel_timestamp_to_item)

    def _timestamp_to_item(self, job: JobBase | None) -> None:
        if self._item is None:
            return None

        if isinstance(self._item, OpenhabItem):
            self._item.oh_post_update(self.next_run_datetime)
        else:
            self._item.post_value(self.next_run_datetime)

    def to_item(self, item: str | BaseValueItem | None) -> None:
        """Sends the next execution (date)time to an item. Sends ``None`` if the job is not scheduled.
        Every time the scheduler updates to a new (date)time the item will also receive the updated time.

        :param item: item name or item, ``None`` to disable
        """
        if item is None:
            self._cancel_timestamp_to_item(None)
            return None

        self._item = Items.get_item(item if not isinstance(item, BaseValueItem) else item.name)
        self._job.on_update.register(self._timestamp_to_item)
        self._job.on_finished.register(self._cancel_timestamp_to_item)
        # Update the item with the current timestamp
        self._timestamp_to_item(None)

    @override
    def cancel(self: Self) -> Self:
        """Cancel the job"""

        run_func_from_async(self._job.job_finish)
        return self

    def get_next_run(self) -> dt_datetime | None:

        warnings.warn(
            'job.get_next_run() is deprecated. Use job.next_run_datetime',
            DeprecationWarning, stacklevel=2
        )
        return self.next_run_datetime

    def remaining(self) -> dt_timedelta | None:

        warnings.warn(
            'job.remaining() is deprecated. Use job.next_run_datetime to get the next execution time or None or'
            ' job.status to see if the job is running or not',
            DeprecationWarning, stacklevel=2
        )
        if (nr := self._job.next_run) is None:
            return None
        return (Instant.now() - nr).py_timedelta()


class CountdownJobControl(HABAppBaseControl):
    def __init__(self, job: CountdownJob) -> None:
        super().__init__()
        self._job: Final[CountdownJob] = job  # type: ignore[misc]

    def set_countdown(self, secs: float) -> Self:
        """Set the countdown time"""
        run_func_from_async(self._job.set_countdown, secs)
        return self

    def stop(self) -> Self:
        """Stop the countdown"""
        run_func_from_async(self._job.job_pause)
        return self

    def reset(self) -> Self:
        """Start the countdown again"""
        run_func_from_async(self._job.reset)
        return self


class OneTimeJobControl(HABAppBaseControl):
    def __init__(self, job: OneTimeJob) -> None:
        super().__init__()
        self._job: Final = job  # type: ignore[misc]


class DateTimeJobControl(HABAppBaseControl):
    def __init__(self, job: DateTimeJob) -> None:
        super().__init__()
        self._job: Final = job  # type: ignore[misc]

    def pause(self) -> Self:
        """Stop executing this job"""
        run_func_from_async(self._job.job_pause)
        return self

    def resume(self) -> Self:
        """Resume executing this job"""
        run_func_from_async(self._job.job_resume)
        return self
