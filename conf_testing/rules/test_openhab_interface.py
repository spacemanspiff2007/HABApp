import random
import string

from HABAppTests import TestBaseRule, ItemWaiter, OpenhabTmpItem, get_openhab_test_types, get_openhab_test_states


class TestOpenhabInterface(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.add_test('Interface item exists', self.test_item_exists)
        self.add_test('Interface item create/remove', self.test_item_create_delete)

        # test the states
        for oh_type in get_openhab_test_types():
            self.add_test( f'post_update {oh_type}', self.test_post_update, oh_type, get_openhab_test_states(oh_type))

    def test_item_exists(self):
        assert not self.openhab.item_exists('item_which_does_not_exist')
        assert self.openhab.item_exists('TestString')

    def test_item_create_delete(self):
        test_item = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        assert not self.openhab.item_exists(test_item)

        self.openhab.create_item('String', test_item)
        assert self.openhab.item_exists(test_item)

        self.openhab.remove_item(test_item)
        assert not self.openhab.item_exists(test_item)

    def test_post_update(self, oh_type, values):
        if isinstance(values, str):
            values = [values]

        with OpenhabTmpItem(None, oh_type) as item, ItemWaiter(item) as waiter:
            for value in values:
                self.openhab.post_update(item, value)
                waiter.wait_for_state(value)

            for value in values:
                if oh_type != 'Contact':
                    self.openhab.send_command(item, value)
                    waiter.wait_for_state(value)

        return waiter.states_ok


TestOpenhabInterface()
