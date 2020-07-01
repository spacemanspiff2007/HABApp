from HABApp.openhab.definitions.helpers.thing_config import ThingConfigChanger


def test_zwave_cfg():
    c = ThingConfigChanger.from_dict({
        'config_1_1': 0,                # 1 byte
        'config_2_2': 0,                # 2 byte
        'config_10_1_wo': 0,            # unclear what wo means
        'config_100_4_000000FF': 0,     # 4 byte with bitmask 0xFF
        'group_1': ['controller'],
    })

    assert 1 in c
    assert 2 in c
    assert 10 in c
    assert 100 in c
    assert 'Group1' in c
