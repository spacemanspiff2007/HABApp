from HABAppTests import EventWaiter, ItemWaiter, OpenhabTmpItem, TestBaseRule
from HABAppTests.errors import TestCaseFailed

from HABApp.openhab.events import ItemStateUpdatedEventFilter
from HABApp.openhab.items import GroupItem, SwitchItem


class TestOpenhabGroupFunction(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.group = OpenhabTmpItem('Group')
        self.item1 = OpenhabTmpItem('Switch')
        self.item2 = OpenhabTmpItem('Switch')

        self.add_test('Group function', self.test_group_update)
        self.add_test('Group member change', self.add_item_to_grp)

    def set_up(self):
        self.item1.create_item(groups=[self.group.name])
        self.item2.create_item(groups=[self.group.name])
        self.group.create_item(group_type='Switch', group_function='OR', group_function_params=['ON', 'OFF'])

    def tear_down(self):
        self.item1.remove()
        self.item2.remove()
        self.group.remove()

    def test_group_update(self):
        item1 = SwitchItem.get_item(self.item1.name)
        item2 = SwitchItem.get_item(self.item2.name)
        group = GroupItem.get_item(self.group.name)

        with ItemWaiter(group) as waiter:
            waiter.wait_for_state(None)

            item1.oh_post_update('ON')
            waiter.wait_for_state('ON')

            item1.oh_post_update('OFF')
            waiter.wait_for_state('OFF')

            item2.oh_post_update('ON')
            waiter.wait_for_state('ON')

    def add_item_to_grp(self):
        new_item = OpenhabTmpItem('Switch')
        try:
            with EventWaiter(self.group.name, ItemStateUpdatedEventFilter()) as w:
                new_item.create_item(groups=[self.group.name])
                event = w.wait_for_event()
                while event.name != self.group.name:
                    w.wait_for_event()
        except TestCaseFailed:
            return None
        finally:
            new_item.remove()

        raise TestCaseFailed(f'Event for group {self.group.name} reveived but expected none!')


TestOpenhabGroupFunction()
