from HABApp.core.events import ValueNoUpdateEvent, ValueNoChangeEvent
from HABApp.core.items import Item
from HABAppTests import TestBaseRule, EventWaiter


class TestItemEvents(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('Item const', self.item_events, changes=False, secs=2, values=['MyVal', 'MyVal', 'MyVal'])
        self.add_test('Item change', self.item_events, changes=True, secs=2, values=['MyVal1', 'MyVal2', 'MyVal3'])

    def item_events(self, changes=False, secs=5, values=[]):
        watch_item = Item.get_create_item('watch_item', values[0])
        event = ValueNoUpdateEvent if not changes else ValueNoChangeEvent

        def cb(event: ValueNoUpdateEvent):
            assert event.name == watch_item.name, f'Wrong name: {event.name} != {watch_item.name}'
            assert event.seconds == secs, f'Wrong seconds: {event.seconds} != {secs}'
        self.item_watch_and_listen(watch_item.name, secs, cb, changes)

        for step, value in enumerate(values):
            watch_item.set_value(value)
            with EventWaiter(watch_item.name, event, secs + 2) as w:
                w.wait_for_event(value)
                if not w.events_ok:
                    return w.events_ok

        return True


TestItemEvents()
