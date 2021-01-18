from HABApp.core.wrappedfunction import WrappedFunction
from HABApp.mqtt.events import MqttValueChangeEvent, MqttValueChangeEventFilter, MqttValueUpdateEvent, \
    MqttValueUpdateEventFilter
from tests.helpers import check_class_annotations


def test_class_annotations():
    """EventFilter relies on the class annotations so we test that every event has those"""

    exclude = ['MqttValueChangeEventFilter', 'MqttValueUpdateEventFilter']
    check_class_annotations('HABApp.mqtt.events', exclude=exclude, skip_imports=False)


def test_create_listener():
    f = MqttValueUpdateEventFilter(value=1)
    e = f.listener_from_filter('asdf', WrappedFunction(lambda x: x))

    assert e.event_filter is MqttValueUpdateEvent
    assert e.attr_name1 == 'value'
    assert e.attr_value1 == 1

    f = MqttValueChangeEventFilter(old_value='asdf')
    e = f.listener_from_filter('asdf', WrappedFunction(lambda x: x))

    assert e.event_filter is MqttValueChangeEvent
    assert e.attr_name1 == 'old_value'
    assert e.attr_value1 == 'asdf'

    f = MqttValueChangeEventFilter(old_value='asdf', value=1)
    e = f.listener_from_filter('asdf', WrappedFunction(lambda x: x))

    assert e.event_filter is MqttValueChangeEvent
    assert e.attr_name1 == 'value'
    assert e.attr_value1 == 1
    assert e.attr_name2 == 'old_value'
    assert e.attr_value2 == 'asdf'
