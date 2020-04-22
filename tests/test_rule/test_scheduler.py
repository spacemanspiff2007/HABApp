import unittest.mock
from datetime import datetime, time, timedelta

from pytz import utc

import HABApp
from HABApp.rule import scheduler


class FuncWrapper:
    mock = unittest.mock.MagicMock()

    def run(self, *args, **kwargs):
        self.mock(*args, **kwargs)


func = FuncWrapper()


def test_one_time():
    func.mock.reset_mock()
    s = scheduler.OneTimeCallback(func)

    s.set_run_time(None)
    s.check_due(datetime.now(tz=utc))
    func.mock.assert_not_called()
    s.execute()
    func.mock.assert_called()


def test_workday():
    func.mock.reset_mock()
    s = scheduler.DayOfWeekScheduledCallback(func)

    s.weekdays('workday')
    s.time(datetime(year=2000, month=12, day=30, hour=12))

    assert s.get_next_call() == datetime(2001, 1, 1, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 2, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 3, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 4, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 5, 12)

    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 8, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 9, 12)


def test_weekend():
    func.mock.reset_mock()
    s = scheduler.DayOfWeekScheduledCallback(func)

    s.weekdays('weekend')
    s.time(datetime(year=2001, month=1, day=1, hour=12))

    assert s.get_next_call() == datetime(2001, 1, 6, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 7, 12)

    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 13, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 14, 12)

    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 20, 12)
    s._calculate_next_call()
    assert s.get_next_call() == datetime(2001, 1, 21, 12)


def test_sun():
    HABApp.CONFIG.location.latitude = 52.52437
    HABApp.CONFIG.location.longitude = 13.41053
    HABApp.CONFIG.location.elevation = 43
    HABApp.CONFIG.location.on_all_values_set()

    func.mock.reset_mock()
    s = scheduler.SunScheduledCallback(func)

    s.sun_trigger('sunrise')
    s._calculate_next_call()
    assert s._next_base.tzinfo is not None

    s.earliest(time(hour=12))
    s._update_run_time()
    assert s._next_call.astimezone(scheduler.base.local_tz).time() == time(12)

    s.earliest(None)
    s.latest(time(hour=2))
    s._update_run_time()
    assert s._next_call.astimezone(scheduler.base.local_tz).time() == time(2)


def cmp_ts(a: datetime, b: datetime):
    diff = abs(a.timestamp() - b.timestamp())
    assert diff < 0.0001, f'Diff: {diff}\n{a}\n{b}'


def test_boundary():
    func.mock.reset_mock()
    s = scheduler.reoccurring_cb.ReoccurringScheduledCallback(func)

    now = datetime.now()
    s.interval(timedelta(seconds=15))
    cmp_ts(s.get_next_call(), now + timedelta(seconds=15))

    def b_func(d: datetime):
        return d + timedelta(seconds=15)

    s.boundary_func(b_func)
    cmp_ts(s.get_next_call(), now + timedelta(seconds=30))

    # offset etc comes after the custom function
    s.offset(timedelta(seconds=-10))
    cmp_ts(s.get_next_call(), now + timedelta(seconds=20))


def test_boundary_func():
    func.mock.reset_mock()
    s = scheduler.reoccurring_cb.ReoccurringScheduledCallback(func)

    now = datetime.now()
    s.interval(timedelta(seconds=15))
    cmp_ts(s.get_next_call(), now + timedelta(seconds=15))

    def b_func(d: datetime):
        s.offset(timedelta(seconds=15))
        return d

    s.boundary_func(b_func)
    cmp_ts(s.get_next_call(), now + timedelta(seconds=30))
