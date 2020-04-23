from HABApp.openhab.definitions.rest.items import GroupFunctionDefinition


def test_or():
    _in = {
        "name": "OR",
        "params": [
            "ON",
            "OFF"
        ]
    }
    o = GroupFunctionDefinition.parse_obj(_in)  # type: GroupFunctionDefinition
    assert o.name == 'OR'
    assert o.params == ['ON', 'OFF']


def test_eq():
    _in = {"name": "EQUALITY"}
    o = GroupFunctionDefinition.parse_obj(_in)  # type: GroupFunctionDefinition
    assert o.name == 'EQUALITY'
    assert o.params is None
