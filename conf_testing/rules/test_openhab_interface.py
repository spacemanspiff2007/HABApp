import random
import string

import HABApp
from HABAppTests import TestBaseRule, ItemWaiter, OpenhabTmpItem, get_openhab_test_types, get_openhab_test_states


class TestOpenhabInterface(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.add_test('Interface item exists', self.test_item_exists)
        self.add_test('Interface item create/remove', self.test_item_create_delete)
        self.add_test('Interface group create/remove', self.test_item_create_delete_group)
        self.add_test('Interface get item definition', self.test_item_definition)

        # test the states
        for oh_type in get_openhab_test_types():
            self.add_test( f'post_update {oh_type}', self.test_post_update, oh_type, get_openhab_test_states(oh_type))

        # test json post
        self.add_test(f'post_update (by_json)', self.test_umlaute)
        self.add_test(f'test_item_not_found', self.test_openhab_item_not_found)

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

    def test_item_create_delete_group(self):
        test_item = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        test_group = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        assert not self.openhab.item_exists(test_item)
        assert not self.openhab.item_exists(test_item)

        self.openhab.create_item('Group', test_group)
        assert self.openhab.item_exists(test_group)
        self.openhab.create_item('String', test_item, groups=[test_group])
        assert self.openhab.item_exists(test_item)

        item = self.openhab.get_item(test_item)
        self.openhab.get_item(test_group)
        assert test_group in item.groups

        self.openhab.remove_item(test_group)
        self.openhab.remove_item(test_item)


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

    def test_umlaute(self):
        LABEL = 'äöß'
        NAME = 'TestUmlaute'

        self.openhab.create_item('String', NAME, label=LABEL)
        ret = self.openhab.get_item(NAME)
        assert ret.label == LABEL

    def test_openhab_item_not_found(self):
        test_item = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        try:
            self.openhab.get_item(test_item)
        except Exception as e:
            if isinstance(e, HABApp.openhab.exceptions.OpenhabItemNotFoundError):
                return True

        return 'Exception not raised!'

    def test_item_definition(self):
        self.openhab.get_item('TestGroupAVG')
        self.openhab.get_item('TestNumber')
        self.openhab.get_item('TestNumber9')
        self.openhab.get_item('TestString')


TestOpenhabInterface()
