# no external dependencies
import typing
import warnings

import HABApp.openhab.errors
import HABApp.openhab.events
import HABApp.openhab.types
from HABApp.core.provider import HABAPP_PROVIDER


# isort: split

# items use the interface for the convenience functions
import HABApp.openhab.items
from HABApp.openhab.connection.handler import OpenHabAsyncInterface, OpenHabSyncInterface


def __getattr__(name: str) -> typing.Any:
    if name == 'interface_async':
        warnings.warn('HABApp.openhab.interface_async is deprecated!', DeprecationWarning, stacklevel=2)
        return HABAPP_PROVIDER.get_existing(OpenHabAsyncInterface)

    if name == 'interface_sync':
        warnings.warn('HABApp.openhab.interface_sync is deprecated!', DeprecationWarning, stacklevel=2)
        return HABAPP_PROVIDER.get_existing(OpenHabSyncInterface)

    return globals()[name]
