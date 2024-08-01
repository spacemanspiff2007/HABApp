from HABApp.mqtt.events import (
    MqttValueChangeEvent,
    MqttValueChangeEventFilter,
    MqttValueUpdateEvent,
    MqttValueUpdateEventFilter,
)
from tests.helpers.inspect import check_class_annotations, get_module_classes


def test_class_annotations():
    """EventFilter relies on the class annotations, so we test that every event has those"""

    exclude = ('MqttValueChangeEventFilter', 'MqttValueUpdateEventFilter')
    for cls in get_module_classes('HABApp.mqtt.events', exclude).values():
        check_class_annotations(cls)


def test_mqtt_filter():
    f = MqttValueUpdateEventFilter(value=1)
    assert f.event_class is MqttValueUpdateEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1

    f = MqttValueChangeEventFilter(old_value='asdf')
    assert f.event_class is MqttValueChangeEvent
    assert f.attr_name1 == 'old_value'
    assert f.attr_value1 == 'asdf'

    f = MqttValueChangeEventFilter(old_value='asdf', value=1)
    assert f.event_class is MqttValueChangeEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1
    assert f.attr_name2 == 'old_value'
    assert f.attr_value2 == 'asdf'
