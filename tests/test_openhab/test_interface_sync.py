from typing import Callable

import pytest

import HABApp.openhab.interface
from HABApp.core.asyncio import async_context, AsyncContextError
from HABApp.openhab.interface import \
    post_update, send_command, \
    get_item, item_exists, remove_item, create_item, \
    get_thing, get_persistence_data, \
    remove_metadata, set_metadata, \
    get_channel_link, remove_channel_link, channel_link_exists, create_channel_link


@pytest.mark.parametrize('func', [
    getattr(HABApp.openhab.interface, i) for i in dir(HABApp.openhab.interface) if i[0] != '_'
])
def test_all_imported(func: Callable):
    assert func.__name__ in globals(), f'"{func.__name__}" not imported!'


@pytest.mark.parametrize('func, args', (
    (post_update,           ('name', 'value')),
    (send_command,          ('name', 'value')),
    (get_item,              ('name', )),
    (get_thing,             ('name', )),
    (item_exists,           ('name', )),
    (remove_item,           ('name', )),
    (create_item,           ('String', 'name')),
    (get_persistence_data,  ('name', None, None, None)),
    (remove_metadata,       ('name', 'ns')),
    (set_metadata,          ('name', 'ns', 'val', {})),
    (get_channel_link,      ('channel', 'item')),
    (channel_link_exists,   ('channel', 'item')),
    (remove_channel_link,   ('channel', 'item')),
    (create_channel_link,   ('channel', 'item', {})),
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
