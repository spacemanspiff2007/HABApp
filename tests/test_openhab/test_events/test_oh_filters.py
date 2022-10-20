from HABApp.openhab.events import ItemStateChangedEvent, ItemStateChangedEventFilter, ItemStateEvent, \
    ItemStateEventFilter, ItemCommandEventFilter, ItemCommandEvent
from tests.helpers.inspect import check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations so we test that every event has those"""

    exclude = ['OpenhabEvent', 'ItemStateChangedEventFilter', 'ItemStateEventFilter', 'ItemCommandEventFilter']
    check_class_annotations('HABApp.openhab.events', exclude=exclude)


def test_oh_filters():

    f = ItemStateEventFilter(value=1)
    assert f.event_class is ItemStateEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1

    f = ItemCommandEventFilter(value=1)
    assert f.event_class is ItemCommandEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1

    f = ItemStateChangedEventFilter(old_value='asdf')
    assert f.event_class is ItemStateChangedEvent
    assert f.attr_name1 == 'old_value'
    assert f.attr_value1 == 'asdf'

    f = ItemStateChangedEventFilter(old_value='asdf', value=1)
    assert f.event_class is ItemStateChangedEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1
    assert f.attr_name2 == 'old_value'
    assert f.attr_value2 == 'asdf'
