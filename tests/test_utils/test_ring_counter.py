import pytest

from HABApp.util.ring_counter import RingCounter, RingCounterTracker


def test_ring_counter() -> None:
    c = RingCounter(10)
    assert c == 0
    assert c.size == 11
    assert len(c) == 11

    c.increase(10)
    assert c == 10
    assert c.value == 10
    assert int(c) == 10

    c.increase(2)
    assert c == 1

    c.increase(12)
    assert c == 2

    c = RingCounter(2, 10, initial_value=9)
    assert c == 9

    c.increase(2)
    assert c == 2

    c.increase(18)
    assert c == 2

    c += 1
    assert c == 3

    c -= 4
    assert c == 8


def test_ring_counter_compare() -> None:
    c = RingCounter(10, initial_value=5)
    assert c == 5

    assert c > 4.9
    assert c >= 5
    assert c >= 4.9999
    assert c < 6
    assert c <= 5.001
    assert c != 6


def test_repr() -> None:
    assert str(RingCounter(10)) == 'RingCounter(value=0, min=0 max=10)'
    assert str(RingCounter(1, 3, initial_value=2)) == 'RingCounter(value=2, min=1 max=3)'

    c = RingCounterTracker(100)
    assert str(c) == 'RingCounterTracker(value=-, min=0, max=100, ignore=10)'
    c.allow(10)
    assert str(c) == 'RingCounterTracker(value=10, min=0, max=100, ignore=10)'


@pytest.mark.parametrize('direction', ('something', 'decreasing'))
def test_ring_counter_init(direction) -> None:
    assert RingCounterTracker(100, direction=direction).allow(0)
    assert RingCounterTracker(100, direction=direction).allow(1)
    assert RingCounterTracker(100, direction=direction).allow(99)
    assert RingCounterTracker(100, direction=direction).allow(100)


def test_ring_counter_tracker_increase() -> None:
    tracker = RingCounterTracker(100)

    ctr = RingCounter(100, initial_value=10)
    c_false = RingCounter(100, initial_value=1)
    c_true = RingCounter(100, initial_value=0)

    values = set()
    for _ in range(1_000):
        assert tracker.allow(ctr.value)
        assert not tracker.allow(c_false.value)
        assert tracker.test_allow(c_true.value)
        for c in (ctr, c_false, c_true):
            c.increase()
        values.add(tracker.value)

    assert values == set(range(101))

    # Test with lower boundary
    tracker = RingCounterTracker(-10, 10)

    ctr = RingCounter(-10, 10, initial_value=10)
    c_false = RingCounter(-10, 10, initial_value=1)
    c_true = RingCounter(-10, 10, initial_value=0)

    values = set()
    for _ in range(1_000):
        assert tracker.allow(ctr.value)
        assert not tracker.allow(c_false.value)
        assert tracker.test_allow(c_true.value)
        for c in (ctr, c_false, c_true):
            c.increase()
        values.add(tracker.value)

    assert values == set(range(-10, 11))




def test_ring_counter_tracker_decrease() -> None:
    tracker = RingCounterTracker(100, direction='decreasing')

    ctr = RingCounter(100, initial_value=20)
    c_false = RingCounter(100, initial_value=29)
    c_true = RingCounter(100, initial_value=30)

    values = set()
    for _ in range(1_000):
        assert tracker.allow(ctr.value)
        assert not tracker.allow(c_false.value)
        assert tracker.test_allow(c_true.value)
        for c in (ctr, c_false, c_true):
            c.decrease()
        values.add(tracker.value)

    assert values == set(range(101))

    # Test with lower boundary
    tracker = RingCounterTracker(20, 40, direction='decreasing')

    ctr = RingCounter(20, 40, initial_value=20)
    c_false = RingCounter(20, 40, initial_value=29)
    c_true = RingCounter(20, 40, initial_value=30)

    values = set()
    for _ in range(1_000):
        assert tracker.allow(ctr.value)
        assert not tracker.allow(c_false.value)
        assert tracker.test_allow(c_true.value)
        for c in (ctr, c_false, c_true):
            c.decrease()
        values.add(tracker.value)

    assert values == set(range(20, 41))


def test_ring_counter_tracker_compare() -> None:
    c = RingCounterTracker(100)
    c.allow(5)
    assert c == 5

    assert c > 4.9
    assert c >= 5
    assert c >= 4.9999
    assert c < 6
    assert c <= 5.001
    assert c != 6
