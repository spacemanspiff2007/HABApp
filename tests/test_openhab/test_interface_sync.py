from datetime import datetime
from typing import Callable

import pytest

import HABApp.openhab.interface_sync
from HABApp.core.asyncio import async_context, AsyncContextError
from HABApp.openhab.interface_sync import \
    post_update, send_command, \
    get_item, item_exists, remove_item, create_item, \
    get_thing, get_persistence_data, get_persistence_services, set_persistence_data, set_thing_enabled, \
    remove_metadata, set_metadata, \
    get_link, remove_link, create_link


@pytest.mark.parametrize('func', [
    getattr(HABApp.openhab.interface_sync, i) for i in dir(HABApp.openhab.interface_sync) if i[0] != '_'
])
def test_all_imported(func: Callable):
    assert func.__name__ in globals(), f'"{func.__name__}" not imported!'


@pytest.mark.parametrize('func, args', (
    (post_update,           ('name', 'value')),
    (send_command,          ('name', 'value')),
    (get_item,              ('name', )),
    (get_thing,             ('name', )),
    (set_thing_enabled,     ('name', True)),
    (item_exists,           ('name', )),
    (remove_item,           ('name', )),
    (create_item,           ('String', 'name')),
    (get_persistence_services,  ()),
    (get_persistence_data,  ('name', None, None, None)),
    (set_persistence_data,  ('name', 'asdf', datetime.now(), None)),
    (remove_metadata,       ('name', 'ns')),
    (set_metadata,          ('name', 'ns', 'val', {})),
    (get_link,              ('item', 'channel')),
    (remove_link,           ('item', 'channel')),
    (create_link,           ('item', 'channel', {})),
))
async def test_item_has_name(func, args):
    async_context.set('Test')

    if func not in (post_update, send_command):
        with pytest.raises(AsyncContextError) as e:
            func(*args)
        assert e.value.func == func
    else:
        # call the function to make sure it doesn't raise an exception
        func(*args)
