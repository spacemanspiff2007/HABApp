from HABApp.mqtt.connection.publish import async_publish, publish
from HABApp.mqtt.connection.subscribe import async_subscribe, subscribe, async_unsubscribe, unsubscribe
from helpers.inspect import assert_same_signature


def test_sync_async_signature():
    assert_same_signature(async_publish, publish)
    assert_same_signature(async_subscribe, subscribe)
    assert_same_signature(async_unsubscribe, unsubscribe)
