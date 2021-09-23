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

            create_item('String', tmpitem.name)
            EventWaiter(tmpitem.name, ItemUpdatedEvent(tmpitem.name, 'String'), 2, False)
            StringItem.get_item(tmpitem.name)

            create_item('DateTime', tmpitem.name)
            EventWaiter(tmpitem.name, ItemUpdatedEvent(tmpitem.name, 'DateTime'), 2, False)
            DatetimeItem.get_item(tmpitem.name)


ChangeItemType()
