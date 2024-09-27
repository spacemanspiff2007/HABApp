from json import dumps

from msgspec.json import decode

from HABApp.openhab.definitions.rest.items import GroupFunctionResp


def test_or() -> None:
    _in = {
        'name': 'OR',
        'params': [
            'ON',
            'OFF'
        ]
    }
    o = decode(dumps(_in), type=GroupFunctionResp)
    assert o.name == 'OR'
    assert o.params == ['ON', 'OFF']


def test_eq() -> None:
    _in = {'name': 'EQUALITY'}
    o = decode(dumps(_in), type=GroupFunctionResp)
    assert o.name == 'EQUALITY'
    assert o.params == []
