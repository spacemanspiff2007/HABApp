from HABApp.core.wrappedfunction import WrappedFunction
from HABApp.openhab.events import ItemStateChangedEvent, ItemStateChangedEventFilter, ItemStateEvent, \
    ItemStateEventFilter
from tests.helpers import check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations so we test that every event has those"""

    exclude = ['OpenhabEvent', 'ItemStateChangedEventFilter', 'ItemStateEventFilter']
    check_class_annotations('HABApp.openhab.events', exclude=exclude, skip_imports=False)


def test_create_listener():

    f = ItemStateEventFilter(value=1)
    e = f.create_event_listener('asdf', WrappedFunction(lambda x: x))

    assert e.event_filter is ItemStateEvent
    assert e.attr_name1 == 'value'
    assert e.attr_value1 == 1

    f = ItemStateChangedEventFilter(old_value='asdf')
    e = f.create_event_listener('asdf', WrappedFunction(lambda x: x))

    assert e.event_filter is ItemStateChangedEvent
    assert e.attr_name1 == 'old_value'
    assert e.attr_value1 == 'asdf'

    f = ItemStateChangedEventFilter(old_value='asdf', value=1)
    e = f.create_event_listener('asdf', WrappedFunction(lambda x: x))

    assert e.event_filter is ItemStateChangedEvent
    assert e.attr_name1 == 'value'
    assert e.attr_value1 == 1
    assert e.attr_name2 == 'old_value'
    assert e.attr_value2 == 'asdf'
