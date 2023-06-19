from HABApp.openhab.events import ItemStateChangedEvent, ItemStateChangedEventFilter, ItemStateUpdatedEventFilter, \
    ItemCommandEventFilter, ItemCommandEvent, ItemStateUpdatedEvent
from tests.helpers.inspect import get_module_classes, check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations, so we test that every event has those"""

    exclude = (
        'OpenhabEvent',
        'ItemStateChangedEventFilter', 'ItemStateUpdatedEventFilter', 'ItemStateEventFilter',
        'ItemCommandEventFilter')
    for cls in get_module_classes('HABApp.openhab.events', exclude).values():
        check_class_annotations(
            cls, init_alias={'initial_value': 'value', 'group_names': 'groups', 'thing_type': 'type'}
        )


def test_oh_filters():

    f = ItemStateUpdatedEventFilter(value=1)
    assert f.event_class is ItemStateUpdatedEvent
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
