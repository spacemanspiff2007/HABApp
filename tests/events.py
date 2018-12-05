import unittest, datetime

from context import HABApp
from HABApp.openhab.events import ItemStateEvent, ItemAddedEvent, ItemCommandEvent, ItemStateChangedEvent, get_event


class TestCases(unittest.TestCase):

    def test_ItemStateEvent(self):
        event = get_event({'topic': 'smarthome/items/Ping/state', 'payload': '{"type":"String","value":"1"}', 'type': 'ItemStateEvent'})
        self.assertIsInstance(event, ItemStateEvent)
        self.assertEqual(event.item, 'Ping')
        self.assertEqual(event.value, '1')


    def test_ItemCommandEvent(self):
        event = get_event({'topic': 'smarthome/items/Ping/command', 'payload': '{"type":"String","value":"1"}', 'type': 'ItemCommandEvent'})
        self.assertIsInstance(event, ItemCommandEvent)
        self.assertEqual(event.item, 'Ping')
        self.assertEqual(event.value, '1')

    def test_ItemAddedEvent(self):
        event = get_event({'topic': 'smarthome/items/TestString/added', 'payload': '{"type":"String","name":"TestString","tags":[],"groupNames":["TestGroup"]}', 'type': 'ItemAddedEvent'})
        self.assertIsInstance(event, ItemAddedEvent)
        self.assertEqual(event.item, 'TestString')

    def test_ItemStateChangedEvent(self):
        event = get_event({'topic': 'smarthome/items/Ping/statechanged', 'payload': '{"type":"String","value":"1","oldType":"UnDef","oldValue":"NULL"}', 'type': 'ItemStateChangedEvent'})
        self.assertIsInstance(event, ItemStateChangedEvent)
        self.assertEqual(event.item, 'Ping')
        self.assertEqual(event.value, '1')

    def test_ItemAddedEvent(self):
        event = get_event({'topic': 'smarthome/items/TestColor_OFF/added', 'payload': '{"type":"Color","name":"TestColor_OFF","tags":[],"groupNames":["TestGroup"]}', 'type': 'ItemAddedEvent'})
        self.assertIsInstance(event, ItemAddedEvent)
        self.assertEqual(event.item, 'TestColor_OFF')

    def test_ItemStateChangedEvent(self):
        d = {'topic': 'smarthome/items/TestDateTimeTOGGLE/statechanged', 'payload': '{"type":"DateTime","value":"2018-11-19T09:47:08.277+0100","oldType":"DateTime","oldValue":"2018-11-19T09:46:38.273+0100"}', 'type': 'ItemStateChangedEvent'}
        event = get_event(d)
        self.assertIsInstance(event, ItemStateChangedEvent)
        self.assertEqual(event.item, 'TestDateTimeTOGGLE')
        self.assertEqual(event.value, datetime.datetime(2018, 11, 19,9,47,8,277000))




if __name__ == '__main__':
    unittest.main()