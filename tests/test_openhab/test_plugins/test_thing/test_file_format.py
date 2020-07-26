from HABApp.openhab.connection_logic.plugin_things.cfg_validator import validate_cfg
from pydantic import ValidationError
import pytest

def test_cfg_optional():
    assert validate_cfg({
        'test': True,
        'filter': {},
    })


def test_cfg_err():
    assert None is validate_cfg({'test': True, 'filter1': {},}, 'filename')
    assert None is validate_cfg({'test': True, 'filter1': {},})


def test_cfg_multiple_filters():
    a = validate_cfg({
        'test': True,
        'filter': {'thing_type': 'bla'},
        'channels': [{'filter': {'channel_uid': 'channel_filter'}}]
    })
    assert a is not None

    b = validate_cfg([{
        'test': True,
        'filter': [{'thing_type': 'bla'}],
        'channels': [{'filter': [{'channel_uid': 'channel_filter'}]}]
    }])
    assert b is not None

    # compare str because we have different instances of the filter class
    assert str(a) == str(b)


def test_cfg_item_builder():
    c = validate_cfg({
        'test': True,
        'filter': {},
        'create items': [
            {'type': 'Switch', 'name': '{thing_uid}'}
        ],
        'channels': [{
            'filter': {},
            'link items': [
                {'type': 'Number', 'name': '{thing_uid}'}
            ],
        }]
    })

    a = list(c[0].get_items({'thing_uid': 'replaced_uid'}))
    assert a[0].type == 'Switch'
    assert a[0].name == 'replaced_uid'

    a = list(c[0].channels[0].get_items({'thing_uid': 'replaced_uid'}))
    assert a[0].type == 'Number'
    assert a[0].name == 'replaced_uid'
