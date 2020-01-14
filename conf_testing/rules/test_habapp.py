from HABApp.core.events import ItemNoUpdateEvent, ItemNoChangeEvent
from HABApp.core.items import Item
from HABAppTests import TestBaseRule, EventWaiter


class TestItemEvents(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('Item const', self.item_events, changes=False, secs=2, values=['MyVal', 'MyVal', 'MyVal'])
        self.add_test('Item change', self.item_events, changes=True, secs=2, values=['MyVal1', 'MyVal2', 'MyVal3'])

    def item_events(self, changes=False, secs=5, values=[]):
        watch_item = Item.get_create_item('watch_item', values[0])
        (watch_item.watch_change if changes else watch_item.watch_update)(secs)
        event = ItemNoUpdateEvent if not changes else ItemNoChangeEvent

        def cb(event: ItemNoUpdateEvent):
            assert event.name == watch_item.name, f'Wrong name: {event.name} != {watch_item.name}'
            assert event.seconds == secs, f'Wrong seconds: {event.seconds} != {secs}'

        self.listen_event(watch_item, cb, event)

        for step, value in enumerate(values):
            watch_item.set_value(value)
            with EventWaiter(watch_item.name, event, secs + 2, check_value=False) as w:
                w.wait_for_event(value)
                if not w.events_ok:
                    return w.events_ok

        return True


TestItemEvents()
