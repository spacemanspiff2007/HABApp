import datetime
import unittest

# from .context import HABApp
from HABApp.openhab.events import ChannelTriggeredEvent, GroupItemStateChangedEvent, ItemAddedEvent, ItemCommandEvent, \
    ItemStateChangedEvent, ItemStateEvent, ItemStatePredictedEvent, ItemUpdatedEvent, get_event


class TestCases(unittest.TestCase):

    def test_ItemStateEvent(self):
        event = get_event({'topic': 'smarthome/items/Ping/state', 'payload': '{"type":"String","value":"1"}',
                           'type': 'ItemStateEvent'})
        self.assertIsInstance(event, ItemStateEvent)
        self.assertEqual(event.name, 'Ping')
        self.assertEqual(event.value, '1')

    def test_ItemCommandEvent(self):
        event = get_event({'topic': 'smarthome/items/Ping/command', 'payload': '{"type":"String","value":"1"}',
                           'type': 'ItemCommandEvent'})
        self.assertIsInstance(event, ItemCommandEvent)
        self.assertEqual(event.name, 'Ping')
        self.assertEqual(event.value, '1')

    def test_ItemAddedEvent1(self):
        event = get_event({'topic': 'smarthome/items/TestString/added',
                           'payload': '{"type":"String","name":"TestString","tags":[],"groupNames":["TestGroup"]}',
                           'type': 'ItemAddedEvent'})
        self.assertIsInstance(event, ItemAddedEvent)
        self.assertEqual(event.name, 'TestString')
        self.assertEqual(event.type, 'String')

    def test_ItemAddedEvent2(self):
        event = get_event({
            'topic': 'smarthome/items/TestColor_OFF/added',
            'payload': '{"type":"Color","name":"TestColor_OFF","tags":[],"groupNames":["TestGroup"]}',
            'type': 'ItemAddedEvent'
        })
        self.assertIsInstance(event, ItemAddedEvent)
        self.assertEqual(event.name, 'TestColor_OFF')
        self.assertEqual(event.type, 'Color')

    def test_ItemUpdatedEvent(self):
        event = get_event({
            'topic': 'smarthome/items/NameUpdated/updated',
            'payload': '[{"type":"Switch","name":"Test","tags":[],"groupNames":[]},'
                       '{"type":"Contact","name":"Test","tags":[],"groupNames":[]}]',
            'type': 'ItemUpdatedEvent'
        })
        self.assertIsInstance(event, ItemUpdatedEvent)
        self.assertEqual(event.name, 'NameUpdated')
        self.assertEqual(event.type, 'Contact')

    def test_ItemStateChangedEvent1(self):
        event = get_event({'topic': 'smarthome/items/Ping/statechanged',
                           'payload': '{"type":"String","value":"1","oldType":"UnDef","oldValue":"NULL"}',
                           'type': 'ItemStateChangedEvent'})
        self.assertIsInstance(event, ItemStateChangedEvent)
        self.assertEqual(event.name, 'Ping')
        self.assertEqual(event.value, '1')
        self.assertEqual(event.old_value, None)

    def test_ItemStatePredictedEvent(self):
        event = get_event({'topic': 'smarthome/items/Buero_Lampe_Vorne_W/statepredicted',
                           'payload': '{"predictedType":"Percent","predictedValue":"10","isConfirmation":false}',
                           'type': 'ItemStatePredictedEvent'})
        self.assertIsInstance(event, ItemStatePredictedEvent)
        self.assertEqual(event.name, 'Buero_Lampe_Vorne_W')
        self.assertEqual(event.value.value, 10.0)

    def test_ItemStateChangedEvent2(self):
        UTC_OFFSET = datetime.datetime.now().astimezone(None).strftime('%z')

        _in = {
            'topic': 'smarthome/items/TestDateTimeTOGGLE/statechanged',
            'payload': f'{{"type":"DateTime","value":"2018-06-21T19:47:08.000{UTC_OFFSET}",'
                       f'"oldType":"DateTime","oldValue":"2017-10-20T17:46:07.000{UTC_OFFSET}"}}',
            'type': 'ItemStateChangedEvent'}

        event = get_event(_in)

        self.assertIsInstance(event, ItemStateChangedEvent)
        self.assertEqual(event.name, 'TestDateTimeTOGGLE')
        self.assertEqual(datetime.datetime(2018, 6, 21, 19, 47, 8), event.value)

    def test_GroupItemStateChangedEvent(self):
        d = {
            'topic': 'smarthome/items/TestGroupAVG/TestNumber1/statechanged',
            'payload': '{"type":"Decimal","value":"16","oldType":"Decimal","oldValue":"15"}',
            'type': 'GroupItemStateChangedEvent'
        }
        event = get_event(d)
        self.assertIsInstance(event, GroupItemStateChangedEvent)
        self.assertEqual(event.name, 'TestGroupAVG')
        self.assertEqual(event.item, 'TestNumber1')
        self.assertEqual(event.value, 16)
        self.assertEqual(event.old_value, 15)

    def test_ChannelTriggeredEvent(self):
        d = {
            "topic": "smarthome/channels/mihome:sensor_switch:00000000000000:button/triggered",
            "payload": "{\"event\":\"SHORT_PRESSED\",\"channel\":\"mihome:sensor_switch:11111111111111:button\"}",
            "type": "ChannelTriggeredEvent"
        }

        event = get_event(d)
        self.assertIsInstance(event, ChannelTriggeredEvent)
        self.assertEqual(event.name, 'mihome:sensor_switch:00000000000000:button')
        self.assertEqual(event.channel, 'mihome:sensor_switch:11111111111111:button')
        self.assertEqual(event.event, 'SHORT_PRESSED')


    def test_thing_info_events(self):
        data = {
            'topic': 'smarthome/things/samsungtv:tv:mysamsungtv/status',
            'payload': '{"status":"ONLINE","statusDetail":"NONE"}',
            'type': 'ThingStatusInfoEvent'
        }
        event = get_event(data)
        assert event.name == 'samsungtv:tv:mysamsungtv'
        assert event.status == 'ONLINE'
        assert event.detail is None

        data = {
            'topic': 'smarthome/things/chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/status',
            'payload': '{"status":"ONLINE","statusDetail":"NONE"}',
            'type': 'ThingStatusInfoEvent'
        }
        event = get_event(data)
        assert event.name == 'chromecast:chromecast:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        assert event.status == 'ONLINE'
        assert event.detail is None

    def test_thing_info_changed_events(self):
        data = {
            'topic': 'smarthome/things/samsungtv:tv:mysamsungtv/statuschanged',
            'payload': '[{"status":"OFFLINE","statusDetail":"NONE"},{"status":"ONLINE","statusDetail":"NONE"}]',
            'type': 'ThingStatusInfoChangedEvent'
        }
        event = get_event(data)
        assert event.name == 'samsungtv:tv:mysamsungtv'
        assert event.status == 'OFFLINE'
        assert event.detail is None
        assert event.old_status == 'ONLINE'
        assert event.old_detail is None

    def test_thing_ConfigStatusInfoEvent(self):
        data = {
            'topic': 'smarthome/things/zwave:device:controller:my_node/config/status',
            'payload': '{"configStatusMessages":[{"parameterName":"switchall_mode","type":"PENDING"}]}',
            'type': 'ConfigStatusInfoEvent'
        }
        event = get_event(data)
        assert event.name == 'zwave:device:controller:my_node'
        assert event.messages == [{"parameterName": "switchall_mode", "type": "PENDING"}]



if __name__ == '__main__':
    unittest.main()
