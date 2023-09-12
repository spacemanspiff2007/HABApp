from msgspec import convert

from HABApp.openhab.definitions.rest.items import ItemResp, StateOptionResp, CommandOptionResp


def test_item_1():
    _in = {
        "link": "http://ip:port/rest/items/Item1Name",
        "state": "CLOSED",
        "transformedState": "zu",
        "stateDescription": {
            "pattern": "MAP(de.map):%s",
            "readOnly": True,
            "options": [
                {"value": "OPEN", "label": "Open"},
                {"value": "CLOSED", "label": "Closed"}]
        },
        "commandDescription": {
            "commandOptions": [
                {"command": "OPEN", "label": "Open"},
                {"command": "CLOSED", "label": "Closed"}
            ]
        },
        "editable": False,
        "type": "Contact",
        "name": "Item1Name",
        "label": "Item1Label",
        "tags": ["Tag1"],
        "groupNames": ["Group1", "Group2"]
    }
    item = convert(_in, type=ItemResp)

    assert item.name == 'Item1Name'
    assert item.label == 'Item1Label'
    assert item.state == 'CLOSED'
    assert item.transformed_state == 'zu'
    assert item.tags == ["Tag1"]
    assert item.groups == ["Group1", "Group2"]


def test_item_2():
    d1 = 'DASDING 98.9 (Euro-Hits)'
    d2 = 'SWR3 95.5 (Top 40/Pop)'

    _in = {"link": "http://openhabian:8080/rest/items/iSbPlayer_Favorit",
           "state": "6",
           "stateDescription": {
               "pattern": "%s",
               "readOnly": False,
               "options": [{"value": "0", "label": d1}, {"value": "1", "label": d2}]
           },
           "commandDescription": {
               "commandOptions": [{"command": "0", "label": d1}, {"command": "1", "label": d2}]
           },
           "editable": False,
           "type": "String",
           "name": "iSbPlayer_Favorit",
           "label": "Senderliste",
           "category": None,
           "tags": [], "groupNames": []}
    item = convert(_in, type=ItemResp)

    assert item.name == 'iSbPlayer_Favorit'
    assert item.label == 'Senderliste'
    assert item.state == '6'
    assert item.transformed_state is None

    desc = item.state_description
    assert desc.pattern == '%s'
    assert desc.read_only is False
    assert desc.options == [StateOptionResp('0', d1), StateOptionResp('1', d2)]

    desc = item.command_description
    assert desc.command_options == [CommandOptionResp('0', d1), CommandOptionResp('1', d2)]


def test_group_item():
    _in = {
        "members": [
            {
                "link": "http://ip:port/rest/items/christmasTree",
                "state": "100",
                "stateDescription": {
                    "minimum": 0, "maximum": 100, "step": 1, "pattern": "%d%%", "readOnly": False, "options": []
                },
                "type": "Dimmer",
                "name": "christmasTree",
                "label": "Christmas Tree",
                "category": "christmas_tree",
                "tags": [],
                "groupNames": ["Group1", "Group2"],
            },
            {
                "link": "http://ip:port/rest/items/frontgardenPower",
                "state": "OFF",
                "stateDescription": {"pattern": "%s", "readOnly": False, "options": []},
                "type": "Switch",
                "name": "frontgardenPower",
                "label": "Outside Power",
                "category": "poweroutlet",
                "tags": [],
                "groupNames": ["Group1", "Group2"],
            }
        ],
        "groupType": "Switch",
        "function": {
            "name": "OR",
            "params": [
                "ON",
                "OFF"
            ]
        },
        "link": "http://ip:port/rest/items/SwitchGroup",
        "state": "ON",
        "editable": False,
        "type": "Group",
        "name": "SwitchGroup",
        "label": "Switch Group",
        "category": "my_category",
        "tags": [],
        "groupNames": [
            "ALL_TOPICS"
        ]
    }
    item = convert(_in, type=ItemResp)

    assert item.name == 'SwitchGroup'
    assert isinstance(item.members[0], ItemResp)
    assert item.members[0].name == 'christmasTree'
    assert item.group_function.name == 'OR'
    assert item.group_function.params == ['ON', 'OFF']
