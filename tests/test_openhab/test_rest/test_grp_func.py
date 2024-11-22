from HABApp.openhab.definitions.rest.items import GroupFunctionResp


def test_or() -> None:
    _in = {
        'name': 'OR',
        'params': [
            'ON',
            'OFF'
        ]
    }

    o = GroupFunctionResp.model_validate(_in)
    assert o.name == 'OR'
    assert o.params == ('ON', 'OFF')


def test_eq() -> None:
    _in = {'name': 'EQUALITY'}
    o = GroupFunctionResp.model_validate(_in)
    assert o.name == 'EQUALITY'
    assert o.params == ()
