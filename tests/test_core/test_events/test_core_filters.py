import pytest

from HABApp.core.event_bus_listener import EventBusListener, WrappedFunction
from HABApp.core.events import EventFilter, ValueChangeEvent, ValueChangeEventFilter, ValueUpdateEvent, \
    ValueUpdateEventFilter
from tests.helpers import check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations so we test that every event has those"""

    check_class_annotations('HABApp.core.events.events', exclude=['ComplexEventValue', 'AllEvents'])


def test_repr():
    f = EventFilter(ValueUpdateEvent, value=1)
    assert str(f) == 'EventFilter(event_type=ValueUpdateEvent, value=1)'

    f = ValueUpdateEventFilter(value='asd')
    assert str(f) == 'ValueUpdateEventFilter(value=asd)'

    f = ValueChangeEventFilter(value=1.5)
    assert str(f) == 'ValueChangeEventFilter(value=1.5)'

    f = ValueChangeEventFilter(old_value=3)
    assert str(f) == 'ValueChangeEventFilter(old_value=3)'

    f = ValueChangeEventFilter(value=1.5, old_value=3)
    assert str(f) == 'ValueChangeEventFilter(value=1.5, old_value=3)'


def test_exception_missing():
    with pytest.raises(AttributeError) as e:
        EventFilter(ValueUpdateEvent, asdf=1)

    assert str(e.value) == 'Filter attribute "asdf" does not exist for "ValueUpdateEvent"'


def test_create_listener():

    f = EventFilter(ValueUpdateEvent, value=1)
    e = EventBusListener('asdf', WrappedFunction(lambda x: x), **f.get_args())

    assert e.event_filter is ValueUpdateEvent
    assert e.prop_name1 == 'value'
    assert e.prop_value1 == 1

    f = ValueChangeEventFilter(old_value='asdf')
    e = EventBusListener('asdf', WrappedFunction(lambda x: x), **f.get_args())

    assert e.event_filter is ValueChangeEvent
    assert e.prop_name1 == 'old_value'
    assert e.prop_value1 == 'asdf'
