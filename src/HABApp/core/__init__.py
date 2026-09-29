import typing

from HABApp.core import asyncio, const, errors, lib, provider, shutdown, types


# isort: split
from HABApp.core import internals, logger, wrapper


# isort: split

import HABApp.core.events
import HABApp.core.files
import HABApp.core.items


# isort: split

from HABApp.core import connections


# isort: split


def __getattr__(name: str) -> typing.Any:
    import warnings  # noqa: PLC0415

    from HABApp.core.internals import EventBus as _EventBusCls  # noqa: PLC0415
    from HABApp.core.internals import ItemRegistry as _ItemRegistryCls
    from HABApp.core.provider import HABAPP_PROVIDER  # noqa: PLC0415

    if name == 'Items':
        warnings.warn('HABApp.core.Items is deprecated!', DeprecationWarning, stacklevel=2)
        return HABAPP_PROVIDER.get_existing(_ItemRegistryCls)

    if name == 'EventBus':
        warnings.warn('HABApp.core.EventBus is deprecated!', DeprecationWarning, stacklevel=2)
        return HABAPP_PROVIDER.get_existing(_EventBusCls)

    return globals()[name]
