from datetime import timedelta as dt_timedelta

import pytest
from whenever import Instant, SystemDateTime, patch_current_time, seconds

from HABApp.core.items.base_valueitem import datetime
from HABApp.core.lib.instant_view import InstantView


@pytest.fixture
def view():
    now = Instant.now().subtract(minutes=1)
    view = InstantView(now.subtract(minutes=1))

    with patch_current_time(now, keep_ticking=False):
        yield view


def test_cmp_instant(view: InstantView) -> None:
    assert view < (now := Instant.now())
    assert view < InstantView(now)
    assert view <= now
    assert view <= InstantView(now)

    assert view > (now := Instant.now().subtract(minutes=1, nanoseconds=1))
    assert view > InstantView(now)
    assert view >= (now := Instant.now().subtract(minutes=1, nanoseconds=1))
    assert view >= InstantView(now)

    assert view == (now := Instant.now().subtract(minutes=1))
    assert view == InstantView(now)
    assert view >= now
    assert view >= InstantView(now)
    assert view <= now
    assert view <= InstantView(now)


def test_add(view: InstantView) -> None:
    now = InstantView.now()
    assert isinstance(view + 1, InstantView)
    assert view + 60 == now
    assert view + 'PT1M' == now
    assert view.add(minutes=1) == now


def test_subtract(view: InstantView) -> None:
    now = InstantView.now()
    assert isinstance(now - 60, InstantView)
    assert now - 'PT1M' == view
    assert now.subtract(minutes=1) == view


def test_older_newer(view: InstantView) -> None:
    assert view.older_than(seconds=59)
    assert view.older_than('PT59S')
    assert view.older_than(59)

    for name in ('seconds', 'minutes', 'hours', 'days'):
        assert view.newer_than(**{name: 61})

    assert view.older_than(InstantView.now())
    assert view.older_than(InstantView.now().subtract(seconds=60, microseconds=-1))

    assert view.newer_than(Instant.now().subtract(minutes=1, nanoseconds=1))
    assert view.newer_than(InstantView.now().subtract(minutes=1, nanoseconds=1))


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
    view = InstantView(s.to_instant())
    assert view.py_datetime() == datetime(2021, 1, 2, 10, 11, 12)


def test_repr() -> None:
    view = InstantView(SystemDateTime(2021, 1, 2, 10, 11, 12).to_instant())
    # Cut the timezone away because we don't know where the test is running
    assert str(view)[:-6] == 'InstantView(2021-01-02T10:11:12+'
