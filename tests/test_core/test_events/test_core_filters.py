from typing import Any

import pytest

from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.events.filter import EventFilter, ValueChangeEventFilter, ValueUpdateEventFilter, NoEventFilter, \
    OrFilterGroup, AndFilterGroup
from tests.helpers.inspect import get_module_classes, check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations, so we test that every event has those"""

    for cls in get_module_classes('HABApp.core.events.events', ('ComplexEventValue', 'AllEvents')).values():
        check_class_annotations(cls)


def test_repr():
    assert NoEventFilter().describe() == 'NoEventFilter()'

    f = EventFilter(ValueUpdateEvent, value=1)
    assert f.describe() == 'EventFilter(type=ValueUpdateEvent, value=1)'

    f = ValueUpdateEventFilter(value='asd')
    assert f.describe() == 'ValueUpdateEventFilter(value=asd)'

    f = ValueChangeEventFilter(value=1.5)
    assert f.describe() == 'ValueChangeEventFilter(value=1.5)'

    f = ValueChangeEventFilter(old_value=3)
    assert f.describe() == 'ValueChangeEventFilter(old_value=3)'

    f = ValueChangeEventFilter(value=1.5, old_value=3)
    assert f.describe() == 'ValueChangeEventFilter(value=1.5, old_value=3)'

    f = AndFilterGroup(ValueChangeEventFilter(old_value=1), ValueChangeEventFilter(value=2))
    assert f.describe() == '(ValueChangeEventFilter(old_value=1) and ValueChangeEventFilter(value=2))'

    f = OrFilterGroup(ValueChangeEventFilter(old_value=1), ValueChangeEventFilter(value=2))
    assert f.describe() == '(ValueChangeEventFilter(old_value=1) or ValueChangeEventFilter(value=2))'


def test_exception_missing():
    with pytest.raises(AttributeError) as e:
        EventFilter(ValueUpdateEvent, asdf=1)

    assert str(e.value) == 'Filter attribute "asdf" does not exist for "ValueUpdateEvent"'


def test_all_events():
    assert NoEventFilter().trigger(None) is True
    assert NoEventFilter().trigger('') is True
    assert NoEventFilter().trigger(False) is True
    assert NoEventFilter().trigger(True) is True
    assert NoEventFilter().trigger('AnyStr') is True


class MyValueUpdateEvent(ValueUpdateEvent):
    def __init__(self, name='asdf', value='asdf'):
        super().__init__(name, value)


class MyValueChangeEvent(ValueChangeEvent):
    def __init__(self, name='asdf', value: Any = 'asdf', old_value: Any = 'asdfasdf'):
        super().__init__(name, value, old_value)


def test_value_change_event_filter():

    f = ValueChangeEventFilter()
    assert f.trigger(MyValueUpdateEvent()) is False
    assert f.trigger(MyValueChangeEvent()) is True

    f = ValueChangeEventFilter(value=1)
    assert f.trigger(MyValueUpdateEvent()) is False
    assert f.trigger(MyValueChangeEvent(value=1)) is True
    assert f.trigger(MyValueChangeEvent(value=2)) is False

    f = ValueChangeEventFilter(old_value=1)
    assert f.trigger(MyValueUpdateEvent()) is False
    assert f.trigger(MyValueChangeEvent(value=1)) is False
    assert f.trigger(MyValueChangeEvent(old_value=2)) is False
    assert f.trigger(MyValueChangeEvent(old_value=1)) is True


def test_filter_groups_and():
    f = AndFilterGroup(ValueChangeEventFilter(old_value=1), ValueChangeEventFilter(value=2))
    assert f.trigger(MyValueUpdateEvent()) is False
    assert f.trigger(MyValueChangeEvent()) is False
    assert f.trigger(MyValueChangeEvent(value=1)) is False
    assert f.trigger(MyValueChangeEvent(value=2)) is False
    assert f.trigger(MyValueChangeEvent(value=2, old_value=3)) is False
    assert f.trigger(MyValueChangeEvent(value=2, old_value=1)) is True


def test_filter_groups_or():
    f = OrFilterGroup(ValueChangeEventFilter(old_value=1), ValueChangeEventFilter(value=2))
    assert f.trigger(MyValueUpdateEvent()) is False
    assert f.trigger(MyValueChangeEvent()) is False
    assert f.trigger(MyValueChangeEvent(value=1)) is False
    assert f.trigger(MyValueChangeEvent(value=2)) is True
    assert f.trigger(MyValueChangeEvent(value=1, old_value=3)) is False
    assert f.trigger(MyValueChangeEvent(value=1, old_value=1)) is True
