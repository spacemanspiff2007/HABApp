from collections.abc import Callable
from datetime import datetime

import pytest

import HABApp.openhab.interface_sync
from HABApp.core.asyncio import AsyncContextError
from HABApp.openhab.interface_sync import (
    create_item,
    create_link,
    get_item,
    get_link,
    get_persistence_data,
    get_persistence_services,
    get_thing,
    item_exists,
    post_update,
    remove_item,
    remove_link,
    remove_metadata,
    send_command,
    set_metadata,
    set_persistence_data,
    set_thing_enabled,
)


@pytest.mark.parametrize('func', [
    getattr(HABApp.openhab.interface_sync, i) for i in dir(HABApp.openhab.interface_sync) if i[0] != '_'
])
def test_all_imported(func: Callable) -> None:
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
async def test_item_has_name(func, args) -> None:

    if func not in (post_update, send_command):
        with pytest.raises(AsyncContextError) as e:
            func(*args)
        assert e.value.func == func
    else:
        # call the function to make sure it doesn't raise an exception
        func(*args)
