from HABApp.openhab.definitions.rest.items import OpenhabItemDefinition


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
    item = OpenhabItemDefinition.parse_obj(_in)  # type: OpenhabItemDefinition

    assert item.name == 'Item1Name'
    assert item.label == 'Item1Label'
    assert item.state == 'CLOSED'
    assert item.transformed_state == 'zu'
    assert item.tags == ["Tag1"]
    assert item.groups == ["Group1", "Group2"]


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
                "groupNames": ["Group1", "Group2"]
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
                "groupNames": ["Group1", "Group2"]
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
    item = OpenhabItemDefinition.parse_obj(_in)   # type: OpenhabItemDefinition

    assert item.name == 'SwitchGroup'
    assert isinstance(item.members[0], OpenhabItemDefinition)
    assert item.members[0].name == 'christmasTree'
