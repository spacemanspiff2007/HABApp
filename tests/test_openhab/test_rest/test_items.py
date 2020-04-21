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
        "tags": [],
        "groupNames": ["Group1", "Group2"]
    }
    item = OpenhabItemDefinition.parse_obj(_in)  # type: OpenhabItemDefinition

    assert item.name == 'Item1Name'
    assert item.label == 'Item1Label'
    assert item.state == 'CLOSED'
    assert item.transformed_state == 'zu'
    assert item.groups == ["Group1", "Group2"]
