from datetime import timedelta as dt_timedelta

import pytest
from whenever import Instant, SystemDateTime, TimeDelta, patch_current_time, seconds

from HABApp.core.items.base_valueitem import datetime
from HABApp.core.lib.instant_view import InstantView


@pytest.fixture
def view():
    now = Instant.now().subtract(minutes=1)
    view = InstantView(now.subtract(minutes=1))

    with patch_current_time(now, keep_ticking=False):
        yield view


def test_methods(view: InstantView):
    assert view < seconds(1)
    assert not view < seconds(60)
    assert view <= seconds(60)

    assert view > seconds(61)
    assert not view > seconds(60)
    assert view >= seconds(60)


def test_cmp_obj(view: InstantView):
    assert view < TimeDelta(seconds=59)
    assert view < dt_timedelta(seconds=59)
    assert view < 'PT59S'
    assert view < 59


def test_cmp_funcs(view: InstantView):
    assert view.older_than(seconds=59)
    assert view.newer_than(seconds=61)


def test_delta_funcs(view: InstantView):
    assert view.delta() == seconds(60)
    assert view.py_timedelta() == dt_timedelta(seconds=60)


def test_convert():
    s = SystemDateTime(2021, 1, 2, 10, 11, 12)
    view = InstantView(s.instant())
    assert view.py_datetime() == datetime(2021, 1, 2, 10, 11, 12)


def test_repr():
    view = InstantView(SystemDateTime(2021, 1, 2, 10, 11, 12).instant())
    assert str(view) == 'InstantView(2021-01-02T10:11:12+01:00)'
