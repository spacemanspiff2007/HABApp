from HABApp.openhab.definitions.rest import ItemChannelLinkDefinition


def test_simple():
    _in = {
        "channelUID": "zwave:device:controller:node15:sensor_luminance",
        "configuration": {},
        "itemName": "ZWaveItem1"
    }
    o = ItemChannelLinkDefinition.from_dict(_in)
    assert o.channel_uid == 'zwave:device:controller:node15:sensor_luminance'
    assert o.item_name == 'ZWaveItem1'


def test_configuration():
    _in = {
        "channelUID": "zwave:device:controller:node15:sensor_luminance",
        "configuration": {
            'profile': 'follow',
            'offset': 1,
        },
        "itemName": "ZWaveItem1"
    }
    o = ItemChannelLinkDefinition.from_dict(_in)
    assert o.channel_uid == 'zwave:device:controller:node15:sensor_luminance'
    assert o.item_name == 'ZWaveItem1'
    assert o.configuration == {'profile': 'follow', 'offset': 1}


def test_creation():

    uid = 'zwave:device:controller:node15:sensor_luminance'
    name = 'ZWaveItem1'

    o = ItemChannelLinkDefinition(item_name=name, channel_uid=uid)
    o.__pydantic_model__.dict(by_alias=True)
    assert o.channel_uid == uid
    assert o.item_name == name
    assert o.configuration == {}

    assert o.to_dict() == {
        "channelUID": "zwave:device:controller:node15:sensor_luminance",
        "itemName": "ZWaveItem1",
        "configuration": {}
    }
