from pytest import fixture, raises

from HABApp.openhab.connection_logic.plugin_things.thing_config import ThingConfigChanger


@fixture
def cfg():
    return ThingConfigChanger.from_dict('UID', {
        'config_1_1': 0,                # 1 byte
        'config_2_2': 0,                # 2 byte
        'config_10_1_wo': 0,            # unclear what wo means
        'config_100_4_000000FF': 0,     # 4 byte with bitmask 0xFF
        'group_1': ['controller'],
    })


def test_zwave_cfg(cfg: ThingConfigChanger):
    assert 1 in cfg
    assert 2 in cfg
    assert 10 in cfg
    assert 100 in cfg
    assert 'Group1' in cfg


def test_set_keys(cfg: ThingConfigChanger):
    cfg[1] = 5

    with raises(KeyError):
        cfg[3] = 7
    with raises(KeyError):
        cfg['1'] = 7
