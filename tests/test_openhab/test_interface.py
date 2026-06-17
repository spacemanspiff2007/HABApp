from datetime import datetime
from unittest.mock import Mock

import pytest

from HABApp.core.asyncio import AsyncContextError
from HABApp.openhab.connection.handler import OpenHabAsyncInterface, OpenHabSyncInterface
from tests.helpers.inspect import assert_same_signature


@pytest.mark.parametrize(('func_name', 'args'), (
    ('post_update',           ('name', 'value')),
    ('send_command',          ('name', 'value')),
    ('get_item',              ('name', )),
    ('get_thing',             ('name', )),
    ('set_thing_enabled',     ('name', True)),
    ('item_exists',           ('name', )),
    ('remove_item',           ('name', )),
    ('create_item',           ('String', 'name')),
    ('get_persistence_services',  ()),
    ('get_persistence_data',  ('name', None, None, None)),
    ('set_persistence_data',  ('name', 'asdf', datetime.now(), None)),
    ('remove_metadata',       ('name', 'ns')),
    ('set_metadata',          ('name', 'ns', 'val', {})),
    ('get_link',              ('item', 'channel')),
    ('remove_link',           ('item', 'channel')),
    ('create_link',           ('item', 'channel', {})),
))
async def test_interface_functions(func_name, args, ir) -> None:

    if_a = OpenHabAsyncInterface(Mock(), Mock(), Mock(), ir)
    if_s = OpenHabSyncInterface(if_a)

    func = getattr(if_s, func_name)

    if func_name not in ('post_update', 'send_command'):
        with pytest.raises(AsyncContextError) as e:
            func(*args)
        assert e.value.func == func
    else:
        # call the function to make sure it doesn't raise an exception
        func(*args)


async def test_same_signature() -> None:

    for name in dir(OpenHabSyncInterface):
        if name.startswith('_'):
            continue

        assert_same_signature(
            getattr(OpenHabSyncInterface, name),
            getattr(OpenHabAsyncInterface, name),
            eval_str=False, check_docstring=False,
            ignore_return=name == 'get_persistence_data'
        )


async def test_complete_implementation() -> None:

    if_a = {name for name in dir(OpenHabAsyncInterface) if not name.startswith('_')}
    if_s = {name for name in dir(OpenHabSyncInterface) if not name.startswith('_')}

    # we don't provide all functions because the users get confused and query openHAB
    # instead of the HABApp item registry which ass a lot of load and delay
    no_sync = {
        'get_items', 'get_items_only_state', 'get_transformations', 'get_things', 'send_websocket_event',
        'get_root_or_none', 'get_system_info_or_none'
    }
    assert not if_s & no_sync

    missing = if_a - if_s - no_sync
    assert not missing, f'Missing functions in OpenHabSyncInterface: {", ".join(sorted(missing))}'

    too_much = if_s - if_a
    assert not too_much
