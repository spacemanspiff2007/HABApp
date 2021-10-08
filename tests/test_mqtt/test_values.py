import pytest
from paho.mqtt.client import MQTTMessage

from HABApp.mqtt.mqtt_payload import get_msg_payload


@pytest.mark.parametrize(
    'payload, expected', (
        ('none', None),
        ('None', None),
        ('true', True),
        ('True', True),
        ('false', False),
        ('False', False),
        ('1', 1),
        ('-1', -1),
        ('0.1', 0.1),
        ('-0.1', -0.1),
        ('asdf', 'asdf'),
        ('[asdf]', '[asdf]'),
        (b'\x07\x07', '\x07\x07'),
    )
)
def test_value_cast(payload, expected):
    msg = MQTTMessage(topic=b'test_topic')
    msg.payload = payload.encode('utf-8') if not isinstance(payload, bytes) else payload
    assert get_msg_payload(msg) == ('test_topic', expected)
