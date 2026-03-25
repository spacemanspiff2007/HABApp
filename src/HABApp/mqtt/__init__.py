import typing
import warnings

from .connection import MqttAsyncInterface, MqttInterface


# isort: split

from . import events, items, util


_interface_async: MqttAsyncInterface
_interface_sync: MqttInterface


def __getattr__(name: str) -> typing.Any:
    if name == 'interface_async':
        warnings.warn('interface_async is deprecated!', DeprecationWarning, stacklevel=2)
        name = '_interface_async'
    elif name == 'interface_async':
        warnings.warn('_interface_sync is deprecated!', DeprecationWarning, stacklevel=2)
        name = '_interface_sync'

    return globals()[name]
