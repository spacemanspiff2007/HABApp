from HABApp.openhab.items import SwitchItem, GroupItem
from HABAppTests import ItemWaiter, TestBaseRule, get_random_name


class TestOpenhabGroupFunction(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.group = get_random_name()
        self.item1 = get_random_name()
        self.item2 = get_random_name()

        self.add_test('Group Update', self.test_group_update)

    def set_up(self):
        self.oh.create_item('Switch', self.item1)
        self.oh.create_item('Switch', self.item2)
        self.oh.create_item('Group', self.group, group_type='Switch', group_function='OR')

    def tear_down(self):
        self.oh.remove_item(self.item1)
        self.oh.remove_item(self.item2)
        self.oh.remove_item(self.group)

    def test_group_update(self):
        item1 = SwitchItem.get_item(self.item1)
        item2 = SwitchItem.get_item(self.item2)
        group = GroupItem(self.group)

        with ItemWaiter(group) as waiter:
            waiter.wait_for_state(None)

            item1.post_value('ON')
            waiter.wait_for_state('ON')

            item1.post_value('OFF')
            waiter.wait_for_state('OFF')

            item2.post_value('ON')
            waiter.wait_for_state('ON')


TestOpenhabGroupFunction()
