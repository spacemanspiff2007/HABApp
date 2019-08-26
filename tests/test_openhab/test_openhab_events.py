import datetime
import unittest

# from .context import HABApp
from HABApp.openhab.events import ItemStateEvent, ItemAddedEvent, ItemCommandEvent,\
    ItemStateChangedEvent, ItemStatePredictedEvent, ItemUpdatedEvent, GroupItemStateChangedEvent, \
    ChannelTriggeredEvent, \
    get_event


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
        self.assertEqual(event.value, 10.0)

    def test_ItemStateChangedEvent2(self):
        d = {
            'topic': 'smarthome/items/TestDateTimeTOGGLE/statechanged',
            'payload': '{"type":"DateTime","value":"2018-11-21T19:47:08.277+0100",'
                       '"oldType":"DateTime","oldValue":"2018-11-19T09:46:38.273+0100"}',
            'type': 'ItemStateChangedEvent'}
        event = get_event(d)
        self.assertIsInstance(event, ItemStateChangedEvent)
        self.assertEqual(event.name, 'TestDateTimeTOGGLE')
        # use this so we don't validate the timezone
        self.assertIsInstance(event.value, datetime.datetime)
        self.assertEqual(event.value.year, 2018)
        self.assertEqual(event.value.month, 11)
        self.assertEqual(event.value.day, 21)
        self.assertEqual(event.value.hour, 19)
        self.assertEqual(event.value.minute, 47)
        self.assertEqual(event.value.second, 8)

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


if __name__ == '__main__':
    unittest.main()
