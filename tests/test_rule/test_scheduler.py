import HABApp
import unittest.mock
from datetime import datetime, date, time

from pytz import utc

from HABApp.rule import scheduler


class FuncWrapper:
    mock = unittest.mock.MagicMock()

    def run(self, *args, **kwargs):
        self.mock(*args, **kwargs)


func = FuncWrapper()


def test_one_time():
    func.mock.reset_mock()
    s = scheduler.OneTimeCallback(func)

    s.set_next_run_time(None)
    s.check_due(datetime.now(tz=utc))
    func.mock.assert_not_called()
    s.execute()
    func.mock.assert_called()


def test_workday():
    func.mock.reset_mock()
    s = scheduler.DayOfWeekScheduledCallback(func)

    s.weekdays('workday')
    s.set_next_run_time(datetime(2001, 1, 1, 12, 30))
    s._calculate_next_call()

    assert s._next_call.date() == date(2001, 1, 2)
    s._calculate_next_call()
    assert s._next_call.date() == date(2001, 1, 3)
    s._calculate_next_call()
    assert s._next_call.date() == date(2001, 1, 4)
    s._calculate_next_call()
    assert s._next_call.date() == date(2001, 1, 5)
    s._calculate_next_call()
    assert s._next_call.date() == date(2001, 1, 8)


def test_weekend():
    func.mock.reset_mock()
    s = scheduler.DayOfWeekScheduledCallback(func)

    s.weekdays('weekend')
    s.set_next_run_time(datetime(2001, 1, 1, 12, 30))
    s._calculate_next_call()

    assert s._next_call.date() == date(2001, 1, 6)
    s._calculate_next_call()
    assert s._next_call.date() == date(2001, 1, 7)
    s._calculate_next_call()
    assert s._next_call.date() == date(2001, 1, 13)


def test_sun():
    HABApp.CONFIG.location.latitude = 52.52437
    HABApp.CONFIG.location.longitude = 13.41053
    HABApp.CONFIG.location.elevation = 43
    HABApp.CONFIG.location.on_all_values_set()

    func.mock.reset_mock()
    s = scheduler.SunScheduledCallback(func)

    s.sun_trigger('sunrise')
    s._calculate_next_call()

    s.earliest(time(hour=12))
    s.update_run_time()
    assert s._next_call.astimezone(scheduler.base.local_tz).time() == time(12)

    s.earliest(None)
    s.latest(time(hour=4))
    s.update_run_time()
    assert s._next_call.astimezone(scheduler.base.local_tz).time() == time(4)
