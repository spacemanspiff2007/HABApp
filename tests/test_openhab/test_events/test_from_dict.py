import datetime, pytest

from HABApp.openhab.events import ChannelTriggeredEvent, GroupItemStateChangedEvent, ItemAddedEvent, ItemCommandEvent, \
    ItemStateChangedEvent, ItemStateEvent, ItemStatePredictedEvent, ItemUpdatedEvent, ThingConfigStatusInfoEvent, \
    ThingStatusInfoChangedEvent, ThingStatusInfoEvent, ThingFirmwareStatusInfoEvent
from HABApp.openhab.map_events import get_event, EVENT_LIST


def test_ItemStateEvent():
    event = get_event({'topic': 'openhab/items/Ping/state', 'payload': '{"type":"String","value":"1"}',
                       'type': 'ItemStateEvent'})
    assert isinstance(event, ItemStateEvent)
    assert event.name == 'Ping'
    assert event.value == '1'


def test_ItemCommandEvent():
    event = get_event({'topic': 'openhab/items/Ping/command', 'payload': '{"type":"String","value":"1"}',
                       'type': 'ItemCommandEvent'})
    assert isinstance(event, ItemCommandEvent)
    assert event.name == 'Ping'
    assert event.value == '1'


def test_ItemAddedEvent1():
    event = get_event({'topic': 'openhab/items/TestString/added',
                       'payload': '{"type":"String","name":"TestString","tags":[],"groupNames":["TestGroup"]}',
                       'type': 'ItemAddedEvent'})
    assert isinstance(event, ItemAddedEvent)
    assert event.name == 'TestString'
    assert event.type == 'String'


def test_ItemAddedEvent2():
    event = get_event({
        'topic': 'openhab/items/TestColor_OFF/added',
        'payload': '{"type":"Color","name":"TestColor_OFF","tags":[],"groupNames":["TestGroup"]}',
        'type': 'ItemAddedEvent'
    })
    assert isinstance(event, ItemAddedEvent)
    assert event.name == 'TestColor_OFF'
    assert event.type == 'Color'


def test_ItemUpdatedEvent():
    event = get_event({
        'topic': 'openhab/items/NameUpdated/updated',
        'payload': '[{"type":"Switch","name":"Test","tags":[],"groupNames":[]},'
                   '{"type":"Contact","name":"Test","tags":[],"groupNames":[]}]',
        'type': 'ItemUpdatedEvent'
    })
    assert isinstance(event, ItemUpdatedEvent)
    assert event.name == 'NameUpdated'
    assert event.type == 'Switch'


def test_ItemStateChangedEvent1():
    event = get_event({'topic': 'openhab/items/Ping/statechanged',
                       'payload': '{"type":"String","value":"1","oldType":"UnDef","oldValue":"NULL"}',
                       'type': 'ItemStateChangedEvent'})
    assert isinstance(event, ItemStateChangedEvent)
    assert event.name == 'Ping'
    assert event.value == '1'
    assert event.old_value is None


def test_ItemStatePredictedEvent():
    event = get_event({'topic': 'openhab/items/Buero_Lampe_Vorne_W/statepredicted',
                       'payload': '{"predictedType":"Percent","predictedValue":"10","isConfirmation":false}',
                       'type': 'ItemStatePredictedEvent'})
    assert isinstance(event, ItemStatePredictedEvent)
    assert event.name == 'Buero_Lampe_Vorne_W'
    assert event.value.value == 10.0


def test_ItemStateChangedEvent2():
    UTC_OFFSET = datetime.datetime.now().astimezone(None).strftime('%z')

    _in = {
        'topic': 'openhab/items/TestDateTimeTOGGLE/statechanged',
        'payload': f'{{"type":"DateTime","value":"2018-06-21T19:47:08.000{UTC_OFFSET}",'
                   f'"oldType":"DateTime","oldValue":"2017-10-20T17:46:07.000{UTC_OFFSET}"}}',
        'type': 'ItemStateChangedEvent'}

    event = get_event(_in)

    assert isinstance(event, ItemStateChangedEvent)
    assert event.name == 'TestDateTimeTOGGLE'
    assert datetime.datetime(2018, 6, 21, 19, 47, 8), event.value


def test_GroupItemStateChangedEvent():
    d = {
        'topic': 'openhab/items/TestGroupAVG/TestNumber1/statechanged',
        'payload': '{"type":"Decimal","value":"16","oldType":"Decimal","oldValue":"15"}',
        'type': 'GroupItemStateChangedEvent'
    }
    event = get_event(d)
    assert isinstance(event, GroupItemStateChangedEvent)
    assert event.name == 'TestGroupAVG'
    assert event.item == 'TestNumber1'
    assert event.value == 16
    assert event.old_value == 15


def test_ChannelTriggeredEvent():
    d = {
        "topic": "openhab/channels/mihome:sensor_switch:00000000000000:button/triggered",
        "payload": "{\"event\":\"SHORT_PRESSED\",\"channel\":\"mihome:sensor_switch:11111111111111:button\"}",
        "type": "ChannelTriggeredEvent"
    }

    event = get_event(d)
    assert isinstance(event, ChannelTriggeredEvent)
    assert event.name == 'mihome:sensor_switch:00000000000000:button'
    assert event.channel == 'mihome:sensor_switch:11111111111111:button'
    assert event.event == 'SHORT_PRESSED'


def test_thing_info_events():
    data = {
        'topic': 'openhab/things/samsungtv:tv:mysamsungtv/status',
        'payload': '{"status":"ONLINE","statusDetail":"MyStatusDetail"}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    assert event.name == 'samsungtv:tv:mysamsungtv'
    assert event.status == 'ONLINE'
    assert event.detail == 'MyStatusDetail'

    data = {
        'topic': 'openhab/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status',
        'payload': '{"status":"ONLINE","statusDetail":"NONE"}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    assert event.name == 'chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    assert event.status == 'ONLINE'
    assert event.detail is None


def test_thing_info_changed_events():
    data = {
        'topic': 'openhab/things/samsungtv:tv:mysamsungtv/statuschanged',
        'payload': '[{"status":"OFFLINE","statusDetail":"NONE"},{"status":"ONLINE","statusDetail":"NONE"}]',
        'type': 'ThingStatusInfoChangedEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoChangedEvent)
    assert event.name == 'samsungtv:tv:mysamsungtv'
    assert event.status == 'OFFLINE'
    assert event.detail is None
    assert event.old_status == 'ONLINE'
    assert event.old_detail is None


def test_thing_ConfigStatusInfoEvent():
    data = {
        'topic': 'openhab/things/zwave:device:controller:my_node/config/status',
        'payload': '{"configStatusMessages":[{"parameterName":"switchall_mode","type":"PENDING"}]}',
        'type': 'ConfigStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingConfigStatusInfoEvent)
    assert event.name == 'zwave:device:controller:my_node'
    assert event.messages == [{"parameterName": "switchall_mode", "type": "PENDING"}]


def test_thing_FirmwareStatusEvent():
    data = {
        'topic': 'openhab/things/zigbee:device:12345678:9abcdefghijklmno/firmware/status',
        'payload':
            '{"thingUID":{"segments":["zigbee","device","12345678","9abcdefghijklmno"]},"firmwareStatus":"UNKNOWN"}',
        'type': 'FirmwareStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingFirmwareStatusInfoEvent)
    assert event.status == 'UNKNOWN'


@pytest.mark.parametrize('cls', [*EVENT_LIST])
def test_event_has_name(cls):
    # this test ensure that alle events have a name argument
    c = cls('asdf')
    assert c.name == 'asdf'
