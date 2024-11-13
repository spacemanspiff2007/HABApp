from HABApp.openhab.definitions.rest import ItemChannelLinkResp


def test_simple() -> None:
    _in = {
        'channelUID': 'zwave:device:controller:node15:sensor_luminance',
        'configuration': {},
        'itemName': 'ZWaveItem1',
        'editable': False,
    }
    o = ItemChannelLinkResp.model_validate(_in)
    assert o.channel == 'zwave:device:controller:node15:sensor_luminance'
    assert o.item == 'ZWaveItem1'


def test_configuration() -> None:
    _in = {
        'channelUID': 'zwave:device:controller:node15:sensor_luminance',
        'configuration': {
            'profile': 'follow',
            'offset': 1,
        },
        'itemName': 'ZWaveItem1',
        'editable': False,
    }
    o = ItemChannelLinkResp.model_validate(_in)
    assert o.channel == 'zwave:device:controller:node15:sensor_luminance'
    assert o.item == 'ZWaveItem1'
    assert o.configuration == {'profile': 'follow', 'offset': 1}
