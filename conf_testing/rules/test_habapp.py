import time
from HABApp.core.events import ItemNoUpdateEvent, ItemNoChangeEvent
from HABApp.core.items import Item
from HABAppTests import TestBaseRule, EventWaiter, get_random_name


class TestItemEvents(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('Item const', self.item_events, changes=False, secs=2, values=['MyVal', 'MyVal', 'MyVal'])
        self.add_test('Item change', self.item_events, changes=True, secs=2, values=['MyVal1', 'MyVal2', 'MyVal3'])

    def check_event(self, event: ItemNoUpdateEvent):
        assert event.name == self.watch_item.name, f'Wrong name: {event.name} != {self.watch_item.name}'
        assert event.seconds == self.secs, f'Wrong seconds: {event.seconds} != {self.secs}'
        dur = time.time() - self.ts_set - self.secs
        assert abs(dur) < 0.3, f'Time wrong: {abs(dur):.2f}'

    def item_events(self, changes=False, secs=5, values=[]):
        self.secs = secs
        self.watch_item = Item.get_create_item(get_random_name())
        (self.watch_item.watch_change if changes else self.watch_item.watch_update)(secs)

        event = ItemNoUpdateEvent if not changes else ItemNoChangeEvent

        self.ts_set = 0
        listener = self.listen_event(self.watch_item, self.check_event, event)

        for step, value in enumerate(values):
            if step:
                time.sleep(0.2)
            self.ts_set = time.time()
            self.watch_item.set_value(value)
            with EventWaiter(self.watch_item.name, event, secs + 2, check_value=False) as w:
                w.wait_for_event(value)
                if not w.events_ok:
                    listener.cancel()
                    return w.events_ok

        listener.cancel()
        return True


TestItemEvents()
