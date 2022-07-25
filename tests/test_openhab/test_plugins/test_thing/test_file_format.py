from HABApp.openhab.connection_logic.plugin_things.cfg_validator import validate_cfg, UserItemCfg
from tests.helpers import TestEventBus


def test_cfg_optional():
    assert validate_cfg({
        'test': True,
        'filter': {},
    })


def test_thing_cfg_types():
    assert validate_cfg({
        'test': True,
        'filter': {},
        'thing config': {
            1: 0,
            2: 'str',
            'Group1': ['asdf']
        },
    })


def test_cfg_err(eb: TestEventBus):
    eb.allow_errors = True
    assert None is validate_cfg({'test': True, 'filter1': {}}, 'filename')
    assert None is validate_cfg({'test': True, 'filter1': {}})


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


def test_item_cfg():

    c = UserItemCfg.parse_obj({
        'type': 'Switch',
        'name': 'asdf',
        'metadata': {'a': 'b'}
    })

    i = c.get_item({})
    assert i.metadata == {'a': {'value': 'b', 'config': {}}}

    c = UserItemCfg.parse_obj({
        'type': 'Switch',
        'name': 'asdf',
        'metadata': {'k': {'value': 'b', 'config': {'d': 'e'}}},
    })

    i = c.get_item({})
    assert i.metadata == {'k': {'value': 'b', 'config': {'d': 'e'}}}
