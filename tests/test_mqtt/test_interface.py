
from HABApp.mqtt.connection.interface import MqttAsyncInterface, MqttInterface
from tests.helpers.inspect import assert_same_signature


def test_sync_async_signature() -> None:
    for name in set(dir(MqttAsyncInterface)) | set(dir(MqttInterface)):
        if name.startswith('_'):
            continue

        assert_same_signature(
            getattr(MqttAsyncInterface, name),
            getattr(MqttInterface, name),
        )
