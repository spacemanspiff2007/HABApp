from HABApp.core import asyncio, const, errors, lib, shutdown, types


# isort: split

# The connection manager has no dependencies - that's why we can set it up before the internals
from HABApp.core.connections import Connections


# isort: split
from HABApp.core import internals, logger, wrapper


# isort: split

import HABApp.core.events
import HABApp.core.files
import HABApp.core.items


# isort: split

Items: 'HABApp.core.internals.ItemRegistry' = internals.proxy.ConstProxyObj('ItemRegistry')
EventBus: 'HABApp.core.internals.EventBus' = internals.proxy.ConstProxyObj('EventBus')
