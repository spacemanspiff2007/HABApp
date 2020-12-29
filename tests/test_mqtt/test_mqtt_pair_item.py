import pytest

from HABApp.mqtt.items.mqtt_pair_item import build_write_topic


def test_name_build():

    assert build_write_topic('zigbee2mqtt/my-bulb/XXX') == 'zigbee2mqtt/my-bulb/set/XXX'

    with pytest.raises(ValueError) as e:
        build_write_topic('asdf')

    assert str(e.value) == 'Can not build write topic for "asdf"'
