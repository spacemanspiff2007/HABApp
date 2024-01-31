from __future__ import annotations

import pytest

from HABApp.core.lib import timeout as timeout_module
from HABApp.core.lib.timeout import Timeout, TimeoutNotRunningError
from tests.helpers import MockedMonotonic


@pytest.fixture()
def time(monkeypatch) -> MockedMonotonic:
    m = MockedMonotonic()
    monkeypatch.setattr(timeout_module, 'monotonic', m.get_time)
    return m


def assert_remaining(t: Timeout, time: float | None):
    if time is None:
        assert t.remaining_or_none() is None
        with pytest.raises(TimeoutNotRunningError):
            t.remaining()
    elif isinstance(time, int):
        assert t.remaining() == time
        assert t.remaining_or_none() == time
    else:
        # prevent rounding errors
        assert abs(t.remaining() - time) < 0.000_000_1
        assert abs(t.remaining_or_none() - time) < 0.000_000_1


def test_timeout_init():

    t = Timeout(5, start=False)
    with pytest.raises(TimeoutNotRunningError):
        assert not t.is_expired()
    assert not t.is_running_and_expired()
    assert not t.is_running()

    assert_remaining(t, None)

    t = Timeout(5)
    assert not t.is_expired()
    assert not t.is_running_and_expired()
    assert t.is_running()
    assert_remaining(t, 5)


def test_running_expired(time):
    t = Timeout(5)
    assert t.is_running()
    assert not t.is_running_and_expired()
    assert not t.is_expired()
    assert_remaining(t, 5)

    time += 4.9
    assert t.is_running()
    assert not t.is_expired()
    assert_remaining(t, 0.1)

    time += 0.1
    assert t.is_running()
    assert t.is_expired()
    assert_remaining(t, 0)

    time += 5
    assert t.is_running()
    assert t.is_expired()
    assert_remaining(t, 0)

    t.stop()
    assert not t.is_running()
    assert not t.is_running_and_expired()
    with pytest.raises(TimeoutNotRunningError):
        assert not t.is_expired()
    assert_remaining(t, None)


def test_start_stop_reset(time):
    t = Timeout(5, start=False)
    assert not t.is_running()
    assert_remaining(t, None)

    t.start()
    assert t.is_running()
    assert_remaining(t, 5)

    time += 2
    t.start()
    assert t.is_running()
    assert_remaining(t, 3)

    t.set_timeout(7)
    assert t.is_running()
    assert_remaining(t, 5)

    t.reset()
    assert t.is_running()
    assert_remaining(t, 7)

    t.stop()
    assert not t.is_running()
    assert_remaining(t, None)

    # reset will only reset a running timeout
    t.reset()
    assert not t.is_running()
    assert_remaining(t, None)

    t.start()
    assert t.is_running()
    assert_remaining(t, 7)


def test_repr(time):
    assert str(Timeout(5, start=False)) == '<Timeout 5.0s>'
    assert str(Timeout(10, start=False)) == '<Timeout 10s>'
    assert str(Timeout(100, start=False)) == '<Timeout 100s>'

    t = Timeout(5, start=True)
    assert str(t) == '<Timeout 0.0/5.0s>'
    time += 0.1
    assert str(t) == '<Timeout 0.1/5.0s>'
    time += 4.8
    assert str(t) == '<Timeout 4.9/5.0s>'
    time += 0.1
    assert str(t) == '<Timeout 5.0/5.0s>'
    time += 99
    assert str(t) == '<Timeout 5.0/5.0s>'

    t = Timeout(10, start=True)
    assert str(t) == '<Timeout 0/10s>'
    time += 0.1
    assert str(t) == '<Timeout 0/10s>'
    time += 0.9
    assert str(t) == '<Timeout 1/10s>'
    time += 8
    assert str(t) == '<Timeout 9/10s>'
    time += 1
    assert str(t) == '<Timeout 10/10s>'
    time += 99
    assert str(t) == '<Timeout 10/10s>'
