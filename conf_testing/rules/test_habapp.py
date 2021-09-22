import time
import HABApp
from HABApp.core.events import ItemNoUpdateEvent, ItemNoChangeEvent, ValueUpdateEvent
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
        assert abs(dur) < 0.05, f'Time wrong: {abs(dur):.2f}'

    def item_events(self, changes=False, secs=5, values=[]):
        item_name = get_random_name('HABApp')
        self.secs = secs
        self.watch_item = Item.get_create_item(item_name)
        watcher = (self.watch_item.watch_change if changes else self.watch_item.watch_update)(secs)

        event = ItemNoUpdateEvent if not changes else ItemNoChangeEvent
        listener = self.listen_event(self.watch_item, self.check_event, event)

        def _run():
            self.ts_set = 0
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
            return True

        if not _run():
            return False

        HABApp.core.Items.pop_item(item_name)
        assert not HABApp.core.Items.item_exists(item_name)
        time.sleep(1)
        self.watch_item = Item.get_create_item(item_name)

        if not _run():
            return False

        listener.cancel()
        watcher.cancel()
        return True


TestItemEvents()


class TestItemListener(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('Item.listen_event', self.trigger_event)

    def check_event(self, event: ValueUpdateEvent):
        assert event.name == self.watch_item.name, f'Wrong name: {event.name} != {self.watch_item.name}'
        assert event.value == 123, f'Wrong value: {event.value} != 123'

    def trigger_event(self):
        self.watch_item = Item.get_create_item(get_random_name('HABApp'))
        listener = self.watch_item.listen_event(self.check_event, ValueUpdateEvent)

        self.run.at(
            1, HABApp.core.EventBus.post_event, self.watch_item.name, ValueUpdateEvent(self.watch_item.name, 123)
        )

        with EventWaiter(self.watch_item.name, ValueUpdateEvent, 2, check_value=True) as w:
            w.wait_for_event(123)
            if not w.events_ok:
                listener.cancel()
                return w.events_ok

        listener.cancel()
        return True


TestItemListener()
