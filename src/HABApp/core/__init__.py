from HABApp.core import const
from HABApp.core import lib
from HABApp.core import errors

# isort: split

from HABApp.core import asyncio

# isort: split

# The connection manager has no dependencies - that's why we can set it up before the internals
from HABApp.core.connections import Connections

# isort: split
from HABApp.core import internals

from HABApp.core import wrapper
from HABApp.core import logger

# isort: split

import HABApp.core.events
import HABApp.core.files
import HABApp.core.items

# isort: split

Items: 'HABApp.core.internals.ItemRegistry' = internals.proxy.ConstProxyObj('ItemRegistry')
EventBus: 'HABApp.core.internals.EventBus' = internals.proxy.ConstProxyObj('EventBus')
