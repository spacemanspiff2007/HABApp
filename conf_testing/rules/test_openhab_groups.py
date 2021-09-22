from HABApp.openhab.items import SwitchItem, GroupItem
from HABAppTests import ItemWaiter, TestBaseRule, OpenhabTmpItem


class TestOpenhabGroupFunction(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.group = OpenhabTmpItem('Group')
        self.item1 = OpenhabTmpItem('Switch')
        self.item2 = OpenhabTmpItem('Switch')

        self.add_test('Group Update', self.test_group_update)

    def set_up(self):
        self.item1.create()
        self.item2.create()
        self.group.create(group_type='Switch', group_function='OR', group_function_params=['ON', 'OFF'])

    def tear_down(self):
        self.item1.remove()
        self.item2.remove()
        self.group.remove()

    def test_group_update(self):
        item1 = SwitchItem.get_item(self.item1.item_name)
        item2 = SwitchItem.get_item(self.item2.item_name)
        group = GroupItem.get_item(self.group.item_name)

        with ItemWaiter(group) as waiter:
            waiter.wait_for_state(None)

            item1.oh_post_update('ON')
            waiter.wait_for_state('ON')

            item1.oh_post_update('OFF')
            waiter.wait_for_state('OFF')

            item2.oh_post_update('ON')
            waiter.wait_for_state('ON')

            return waiter.states_ok


TestOpenhabGroupFunction()
