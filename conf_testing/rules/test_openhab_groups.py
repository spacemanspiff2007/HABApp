from HABApp.openhab.items import SwitchItem, GroupItem
from HABAppTests import ItemWaiter, TestBaseRule, get_random_name


class TestOpenhabGroupFunction(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.group = 'Group_' + get_random_name()
        self.item1 = 'Item1_' + get_random_name()
        self.item2 = 'Item2_' + get_random_name()

        self.add_test('Group Update', self.test_group_update)

    def set_up(self):
        self.oh.create_item('Switch', self.item1, groups=[self.group])
        self.oh.create_item('Switch', self.item2, groups=[self.group])
        self.oh.create_item('Group', self.group, group_type='Switch',
                            group_function='OR', group_function_params=['ON', 'OFF'])

    def tear_down(self):
        self.oh.remove_item(self.item1)
        self.oh.remove_item(self.item2)
        self.oh.remove_item(self.group)

    def test_group_update(self):
        item1 = SwitchItem.get_item(self.item1)
        item2 = SwitchItem.get_item(self.item2)
        group = GroupItem.get_item(self.group)

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
