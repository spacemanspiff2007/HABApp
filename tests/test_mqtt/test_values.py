import pytest
from aiomqtt import Message

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
    payload = payload.encode('utf-8') if not isinstance(payload, bytes) else payload
    msg = Message('test_topic', payload, None, None, None, None)
    assert get_msg_payload(msg) == ('test_topic', expected)
