from HABApp.openhab.connection.plugins import WebsocketPlugin
from HABApp.openhab.definitions.websockets import OPENHAB_EVENT_TYPE


def test_type_adapter() -> None:
    res = WebsocketPlugin._get_event_type_names_from_union(OPENHAB_EVENT_TYPE)
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
