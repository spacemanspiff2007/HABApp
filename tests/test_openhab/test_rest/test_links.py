from HABApp.openhab.definitions.rest import ItemChannelLinkDefinition


def test_or():
    _in = {
        "channelUID": "zwave:device:controller:node15:sensor_luminance",
        "configuration": {},
        "itemName": "ZWaveItem1"
    }
    o = ItemChannelLinkDefinition.parse_obj(_in)  # type: ItemChannelLinkDefinition
    assert o.channel_uid == 'zwave:device:controller:node15:sensor_luminance'
    assert o.item_name == 'ZWaveItem1'
