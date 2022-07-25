from HABApp.core.events import EventFilter
from HABApp.openhab.definitions.topics import TOPIC_ITEMS
from HABApp.openhab.events import ItemUpdatedEvent
from HABApp.openhab.interface import create_item
from HABApp.openhab.items import StringItem, NumberItem, DatetimeItem
from HABAppTests import TestBaseRule, OpenhabTmpItem, EventWaiter


class ChangeItemType(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('change_item', self.change_item)

    def change_item(self):
        with OpenhabTmpItem('Number') as tmpitem:
            NumberItem.get_item(tmpitem.name)

            with EventWaiter(TOPIC_ITEMS, EventFilter(ItemUpdatedEvent), 2) as e:
                create_item('String', tmpitem.name)
                e.wait_for_event(type='String', name=tmpitem.name)
            StringItem.get_item(tmpitem.name)

            with EventWaiter(TOPIC_ITEMS, EventFilter(ItemUpdatedEvent), 2) as e:
                create_item('DateTime', tmpitem.name)
                e.wait_for_event(type='DateTime', name=tmpitem.name)
            DatetimeItem.get_item(tmpitem.name)


ChangeItemType()
