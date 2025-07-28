from HABApp.openhab.definitions.helpers import get_discriminator_values_from_union
from HABApp.openhab.definitions.websockets import OpenHabEventType


def test_type_adapter() -> None:
    res = get_discriminator_values_from_union(OpenHabEventType, allow_multiple=('WebSocketEvent', ))
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
