import unittest

from HABApp.core import Events, EventBusListener, wrappedfunction


class TestEvent():
    pass


class TestCasesItem(unittest.TestCase):

    def tearDown(self) -> None:
        Events.remove_all_listeners()

    def setUp(self) -> None:
        Events.remove_all_listeners()
        self.last_event = None

    def event_cb(self, event):
        self.last_event = event

    def test_event_bus(self):
        listener = EventBusListener('test', wrappedfunction.WrappedFunction(self.event_cb))
        Events.add_listener(listener)

        self.assertIs(self.last_event, None)
        for _ in range(10):
            event = TestEvent
            Events.post_event('test', event)
            self.assertIs(self.last_event, event)

        Events.remove_listener(listener)


if __name__ == '__main__':
    unittest.main()
