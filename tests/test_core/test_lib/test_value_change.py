from __future__ import annotations

from HABApp.core.lib import ValueChange


def test_change() -> None:
    assert not ValueChange().changed

    c = ValueChange[int]()
    assert not c.changed

    assert c.set_value(1).changed
    assert c.value == 1
    for _ in range(100):
        assert not c.set_value(1).changed
        assert c.value == 1

    assert c.set_value(2).changed
    assert c.value == 2
    for _ in range(100):
        assert not c.set_value(2).changed
        assert c.value == 2


def test_missing() -> None:
    c = ValueChange[int]()
    assert c.set_value(1)

    assert c.set_missing().changed
    assert c.is_missing

    for _ in range(100):
        assert not c.set_missing().changed
        assert c.is_missing

    assert c.set_value(1).changed
    assert not c.is_missing
    assert c.value == 1


def test_repr() -> None:
    c = ValueChange[int]()
    assert str(c) == '<ValueChange value: <Missing> changed: False>'

    c.set_value(1)
    assert str(c) == '<ValueChange value: 1 changed: True>'

    c.set_value(1)
    assert str(c) == '<ValueChange value: 1 changed: False>'

    c.set_missing()
    assert str(c) == '<ValueChange value: <Missing> changed: True>'

    c.set_missing()
    assert str(c) == '<ValueChange value: <Missing> changed: False>'
