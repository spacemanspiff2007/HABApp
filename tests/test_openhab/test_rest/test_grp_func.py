from HABApp.openhab.definitions.rest.items import GroupFunctionDefinition


def test_or():
    _in = {
        "name": "OR",
        "params": [
            "ON",
            "OFF"
        ]
    }
    o = GroupFunctionDefinition.model_validate(_in)
    assert o.name == 'OR'
    assert o.params == ['ON', 'OFF']


def test_eq():
    _in = {"name": "EQUALITY"}
    o = GroupFunctionDefinition.model_validate(_in)
    assert o.name == 'EQUALITY'
    assert o.params is None
