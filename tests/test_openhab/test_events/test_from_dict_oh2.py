import datetime, pytest

import HABApp.openhab.events
from HABApp.openhab.events import ChannelTriggeredEvent, GroupItemStateChangedEvent, ItemAddedEvent, ItemCommandEvent, \
    ItemStateChangedEvent, ItemStateEvent, ItemStatePredictedEvent, ItemUpdatedEvent, ThingConfigStatusInfoEvent, \
    ThingStatusInfoChangedEvent, ThingStatusInfoEvent
from HABApp.openhab.map_events import get_event
from HABApp.openhab.connection_handler.http_connection import patch_for_oh2


@pytest.fixture
def oh2_event():
    patch_for_oh2()
    yield None
    patch_for_oh2(reverse=True)


def test_ItemStateEvent(oh2_event):
    event = get_event({'topic': 'smarthome/items/Ping/state', 'payload': '{"type":"String","value":"1"}',
                       'type': 'ItemStateEvent'})
    assert isinstance(event, ItemStateEvent)
    assert event.name == 'Ping'
    assert event.value == '1'


def test_ItemCommandEvent(oh2_event):
    event = get_event({'topic': 'smarthome/items/Ping/command', 'payload': '{"type":"String","value":"1"}',
                       'type': 'ItemCommandEvent'})
    assert isinstance(event, ItemCommandEvent)
    assert event.name == 'Ping'
    assert event.value == '1'


def test_ItemAddedEvent1(oh2_event):
    event = get_event({'topic': 'smarthome/items/TestString/added',
                       'payload': '{"type":"String","name":"TestString","tags":[],"groupNames":["TestGroup"]}',
                       'type': 'ItemAddedEvent'})
    assert isinstance(event, ItemAddedEvent)
    assert event.name == 'TestString'
    assert event.type == 'String'


def test_ItemAddedEvent2(oh2_event):
    event = get_event({
        'topic': 'smarthome/items/TestColor_OFF/added',
        'payload': '{"type":"Color","name":"TestColor_OFF","tags":[],"groupNames":["TestGroup"]}',
        'type': 'ItemAddedEvent'
    })
    assert isinstance(event, ItemAddedEvent)
    assert event.name == 'TestColor_OFF'
    assert event.type == 'Color'


def test_ItemUpdatedEvent(oh2_event):
    event = get_event({
        'topic': 'smarthome/items/NameUpdated/updated',
        'payload': '[{"type":"Switch","name":"Test","tags":[],"groupNames":[]},'
                   '{"type":"Contact","name":"Test","tags":[],"groupNames":[]}]',
        'type': 'ItemUpdatedEvent'
    })
    assert isinstance(event, ItemUpdatedEvent)
    assert event.name == 'NameUpdated'
    assert event.type == 'Switch'


def test_ItemStateChangedEvent1(oh2_event):
    event = get_event({'topic': 'smarthome/items/Ping/statechanged',
                       'payload': '{"type":"String","value":"1","oldType":"UnDef","oldValue":"NULL"}',
                       'type': 'ItemStateChangedEvent'})
    assert isinstance(event, ItemStateChangedEvent)
    assert event.name == 'Ping'
    assert event.value == '1'
    assert event.old_value is None


def test_ItemStatePredictedEvent(oh2_event):
    event = get_event({'topic': 'smarthome/items/Buero_Lampe_Vorne_W/statepredicted',
                       'payload': '{"predictedType":"Percent","predictedValue":"10","isConfirmation":false}',
                       'type': 'ItemStatePredictedEvent'})
    assert isinstance(event, ItemStatePredictedEvent)
    assert event.name == 'Buero_Lampe_Vorne_W'
    assert event.value.value == 10.0


def test_ItemStateChangedEvent2(oh2_event):
    UTC_OFFSET = datetime.datetime.now().astimezone(None).strftime('%z')

    _in = {
        'topic': 'smarthome/items/TestDateTimeTOGGLE/statechanged',
        'payload': f'{{"type":"DateTime","value":"2018-06-21T19:47:08.000{UTC_OFFSET}",'
                   f'"oldType":"DateTime","oldValue":"2017-10-20T17:46:07.000{UTC_OFFSET}"}}',
        'type': 'ItemStateChangedEvent'}

    event = get_event(_in)

    assert isinstance(event, ItemStateChangedEvent)
    assert event.name == 'TestDateTimeTOGGLE'
    assert datetime.datetime(2018, 6, 21, 19, 47, 8), event.value


def test_GroupItemStateChangedEvent(oh2_event):
    d = {
        'topic': 'smarthome/items/TestGroupAVG/TestNumber1/statechanged',
        'payload': '{"type":"Decimal","value":"16","oldType":"Decimal","oldValue":"15"}',
        'type': 'GroupItemStateChangedEvent'
    }
    event = get_event(d)
    assert isinstance(event, GroupItemStateChangedEvent)
    assert event.name == 'TestGroupAVG'
    assert event.item == 'TestNumber1'
    assert event.value == 16
    assert event.old_value == 15


def test_ChannelTriggeredEvent(oh2_event):
    d = {
        "topic": "smarthome/channels/mihome:sensor_switch:00000000000000:button/triggered",
        "payload": "{\"event\":\"SHORT_PRESSED\",\"channel\":\"mihome:sensor_switch:11111111111111:button\"}",
        "type": "ChannelTriggeredEvent"
    }

    event = get_event(d)
    assert isinstance(event, ChannelTriggeredEvent)
    assert event.name == 'mihome:sensor_switch:00000000000000:button'
    assert event.channel == 'mihome:sensor_switch:11111111111111:button'
    assert event.event == 'SHORT_PRESSED'


def test_thing_info_events(oh2_event):
    data = {
        'topic': 'smarthome/things/samsungtv:tv:mysamsungtv/status',
        'payload': '{"status":"ONLINE","statusDetail":"MyStatusDetail"}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    assert event.name == 'samsungtv:tv:mysamsungtv'
    assert event.status == 'ONLINE'
    assert event.detail == 'MyStatusDetail'

    data = {
        'topic': 'smarthome/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status',
        'payload': '{"status":"ONLINE","statusDetail":"NONE"}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    assert event.name == 'chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    assert event.status == 'ONLINE'
    assert event.detail is None


def test_thing_info_changed_events(oh2_event):
    data = {
        'topic': 'smarthome/things/samsungtv:tv:mysamsungtv/statuschanged',
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


def test_thing_ConfigStatusInfoEvent(oh2_event):
    data = {
        'topic': 'smarthome/things/zwave:device:controller:my_node/config/status',
        'payload': '{"configStatusMessages":[{"parameterName":"switchall_mode","type":"PENDING"}]}',
        'type': 'ConfigStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingConfigStatusInfoEvent)
    assert event.name == 'zwave:device:controller:my_node'
    assert event.messages == [{"parameterName": "switchall_mode", "type": "PENDING"}]
