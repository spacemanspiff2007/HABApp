import typing
import warnings

from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.mqtt.connection import MqttAsyncInterface, MqttInterface


# isort: split

from HABApp.mqtt import events, items, util


def __getattr__(name: str) -> typing.Any:
    if name == 'interface_async':
        warnings.warn('HABApp.mqtt.interface_async is deprecated!', DeprecationWarning, stacklevel=2)
        return HABAPP_PROVIDER.get_existing(MqttAsyncInterface)

    if name == 'interface_sync':
        warnings.warn('HABApp.mqtt.interface_sync is deprecated!', DeprecationWarning, stacklevel=2)
        return HABAPP_PROVIDER.get_existing(MqttInterface)

    return globals()[name]
