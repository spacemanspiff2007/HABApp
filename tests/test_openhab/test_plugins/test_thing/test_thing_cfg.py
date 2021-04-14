from pytest import fixture, raises

from HABApp.openhab.connection_logic.plugin_things.thing_config import ThingConfigChanger


@fixture
def cfg():
    return ThingConfigChanger.from_dict('UID', {
        'config_1_1': 0,                # 1 byte
        'config_2_2': 0,                # 2 byte
        'config_10_1_wo': 0,            # unclear what wo means
        'config_100_4_000000FF': 0,     # 4 byte with bitmask 0xFF

        # sometimes parameters are inside the dict multiple times with a bitmask
        "config_154_4_00FF0000": 255,
        "config_154_4": 4294967295,
        "config_154_4_7F000000": 127,
        "config_154_4_000000FF": 255,
        "config_154_4_0000FF00": 255,

        'group_1': ['controller'],

        'binding_cmdrepollperiod': 2600,
        "wakeup_interval": 3600,
    })


def test_zwave_cfg(cfg: ThingConfigChanger):
    assert 1 in cfg
    assert 2 in cfg
    assert 10 in cfg
    assert 100 in cfg
    assert 'Group1' in cfg


def test_param_split(cfg: ThingConfigChanger):
    assert 154 in cfg
    assert cfg.alias[154] == 'config_154_4'

    assert '154_7F000000' in cfg
    assert cfg.alias['154_7F000000'] == 'config_154_4_7F000000'

    assert '154_00FF0000' in cfg
    assert cfg.alias['154_00FF0000'] == 'config_154_4_00FF0000'

    assert '154_0000FF00' in cfg
    assert cfg.alias['154_0000FF00'] == 'config_154_4_0000FF00'

    assert '154_000000FF' in cfg
    assert cfg.alias['154_000000FF'] == 'config_154_4_000000FF'


def test_set_keys(cfg: ThingConfigChanger):
    cfg[1] = 5
    cfg['wakeup_interval'] = 7200

    with raises(KeyError):
        cfg[3] = 7

    with raises(KeyError):
        cfg['1'] = 7


def test_set_wrong_type(cfg: ThingConfigChanger):
    with raises(ValueError) as e:
        cfg[1] = "asdf"
    assert str(e.value) == "Datatype of parameter '1' must be 'int' but is 'str': 'asdf'"

    with raises(ValueError):
        cfg['Group1'] = 'asdf'


def test_eval(cfg: ThingConfigChanger):
    # This resolves to the default
    cfg[100] = '$1 * 20 + $10'
    assert cfg.new == {}

    cfg[1] = 2
    cfg[10] = 3

    cfg[100] = '$1 * 20 + $10'
    assert cfg.new['config_100_4_000000FF'] == 43

    with raises(KeyError) as e:
        cfg[100] = '$1 * 20 + $11'
    assert e.value.args[0] == 'Reference "11" in "$1 * 20 + $11" does not exist for UID!'

    cfg[100] = 'int($1 * 20 + $10)'

    # Test reference to non z-wave param
    cfg[100] = 'int($binding_cmdrepollperiod // 1000)'
