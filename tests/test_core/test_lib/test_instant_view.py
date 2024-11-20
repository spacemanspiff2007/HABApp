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


def test_methods(view: InstantView) -> None:
    assert view > seconds(59)
    assert not view > seconds(60)
    assert view >= seconds(60)

    assert view < seconds(61)
    assert not view < seconds(60)
    assert view <= seconds(60)


def test_cmp_obj(view: InstantView) -> None:
    assert view > TimeDelta(seconds=59)
    assert view > dt_timedelta(seconds=59)
    assert view > 'PT59S'
    assert view > 59

    assert view < Instant.now()
    assert view < InstantView.now()
    assert view == Instant.now().subtract(minutes=1)


def test_cmp_funcs(view: InstantView) -> None:
    assert view.older_than(seconds=59)
    assert view > 59
    assert view >= 60

    assert view.newer_than(seconds=61)
    assert view < 61
    assert view <= 60


def test_delta_funcs(view: InstantView) -> None:
    assert view.delta_now() == seconds(60)
    assert view.py_timedelta() == dt_timedelta(seconds=60)

    assert view.delta_now(Instant.now()) == seconds(60)
    assert view.delta_now(InstantView.now()) == seconds(60)

    with pytest.raises(ValueError) as e:
        view.delta_now(Instant.now().subtract(minutes=2))
    assert str(e.value) == 'Reference instant must be newer than the instant of the InstantView'


def test_convert() -> None:
    s = SystemDateTime(2021, 1, 2, 10, 11, 12)
    view = InstantView(s.instant())
    assert view.py_datetime() == datetime(2021, 1, 2, 10, 11, 12)


def test_repr() -> None:
    view = InstantView(SystemDateTime(2021, 1, 2, 10, 11, 12).instant())
    # Cut the timezone away because we don't know where the test is running
    assert str(view)[:-6] == 'InstantView(2021-01-02T10:11:12+'
