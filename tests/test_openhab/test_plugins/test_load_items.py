import logging

from HABApp.core.internals import ItemRegistry
from HABApp.openhab.connection_logic.plugin_load_items import LoadAllOpenhabItems
import HABApp.openhab.connection_logic.plugin_load_items as plugin_load_items


async def _mock_get_items(all_metadata=False, only_item_state=False):

    if all_metadata:
        return [
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

    if only_item_state:
        return [
            {"type": "Number:Length", "name": "ItemLength", "state": "5 m"},
            {"type": "Number", "name": "ItemPlain", "state": "3.14"}
        ]

    raise ValueError()


async def test_item_sync(monkeypatch, ir: ItemRegistry, test_logs):
    monkeypatch.setattr(plugin_load_items, 'async_get_items', _mock_get_items)

    await LoadAllOpenhabItems().load_items()

    assert [(i.name, i.value) for i in ir.get_items()] == [
        ('ItemLength', 5), ('ItemPlain', 3.14), ('ItemNoUpdate', None)]

    test_logs.add_expected('HABApp.openhab.items', logging.WARNING,
                           'Item ItemLength is a UoM item but "unit" is not found in item metadata')
