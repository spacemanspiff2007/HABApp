from HABApp.openhab.connection.plugins import WebsocketPlugin


def test_type_adapter() -> None:
    res = WebsocketPlugin._get_type_names_from_adapter()
    assert res == [
        'ChannelDescriptionChangedEvent',
        'ChannelTriggeredEvent',
        'ConfigStatusInfoEvent',
        'FirmwareStatusInfoEvent',
        'GroupItemStateChangedEvent',
        'GroupStateUpdatedEvent',
        'ItemAddedEvent',
        'ItemCommandEvent',
        'ItemRemovedEvent',
        'ItemStateChangedEvent',
        'ItemStateEvent',
        'ItemStatePredictedEvent',
        'ItemStateUpdatedEvent',
        'ItemUpdatedEvent',
        'ThingAddedEvent',
        'ThingRemovedEvent',
        'ThingStatusInfoChangedEvent',
        'ThingStatusInfoEvent',
        'ThingUpdatedEvent',
        'WebSocketEvent'
    ]
