import logging
from json import dumps
from typing import List

import msgspec.json

from HABApp.core.internals import ItemRegistry
from HABApp.openhab.connection.plugins import LoadOpenhabItemsPlugin
from HABApp.openhab.connection.connection import OpenhabContext
import HABApp.openhab.connection.plugins.load_items as load_items_module
from HABApp.openhab.definitions.rest import ShortItemResp, ItemResp


async def _mock_get_all_items():
    resp = [
        {
            "link": "link length",
            "state": "NULL",
            "stateDescription": {
                "pattern": "%d",
                "readOnly": True,
                "options": []
            },
            "metadata": {
                "autoupdate": {
                    "value": "false"
                }
            },
            "editable": False,
            "type": "Number:Length",
            "name": "ItemLength",
            "label": "Label length",
            "tags": [],
            "groupNames": ["grp1"]
        },
        {
            "link": "link plain",
            "state": "NULL",
            "editable": False,
            "type": "Number",
            "name": "ItemPlain",
            "label": "Label plain",
            "tags": [],
            "groupNames": []
        },
        {
            "link": "link no update",
            "state": "NULL",
            "editable": False,
            "type": "Number",
            "name": "ItemNoUpdate",
            "tags": [],
            "groupNames": []
        },
    ]

    return msgspec.json.decode(dumps(resp), type=List[ItemResp])


async def _mock_get_all_items_state():
    return [
        ShortItemResp("Number:Length", "ItemLength", "5 m"),
        ShortItemResp("Number", "ItemPlain", "3.14")
    ]


async def _mock_get_things():
    return []


async def test_item_sync(monkeypatch, ir: ItemRegistry, test_logs):
    monkeypatch.setattr(load_items_module, 'async_get_items', _mock_get_all_items)
    monkeypatch.setattr(load_items_module, 'async_get_all_items_state', _mock_get_all_items_state)
    monkeypatch.setattr(load_items_module, 'async_get_things', _mock_get_things)

    context = OpenhabContext(
        version=(1, 0, 0), is_oh3=False,
        waited_for_openhab=False,
        created_items={}, created_things={},

        session=None, session_options=None,

        workaround_small_floats=False
    )
    # initial item create
    await LoadOpenhabItemsPlugin().on_connected(context)

    # sync state
    await LoadOpenhabItemsPlugin().on_connected(context)

    assert [(i.name, i.value) for i in ir.get_items()] == [
        ('ItemLength', 5), ('ItemPlain', 3.14), ('ItemNoUpdate', None)]

    test_logs.add_expected('HABApp.openhab.items', logging.WARNING,
                           'Item ItemLength is a UoM item but "unit" is not found in item metadata')
