# ----------------------------------------------------------------------------------------------------------------------
# This rule requires the following items:
# ----------------------------------------------------------------------------------------------------------------------
#
# Group				TestGroup
# Group:Number:AVG 	TestGroupAVG
#
# String    TestString  (TestGroup)  				[TestTag]  {meta1="test" [key="value"]}
# Number	TestNumber	(TestGroup, TestGroupAVG)
#
# ----------------------------------------------------------------------------------------------------------------------
import time

from HABAppTests import (
    EventWaiter,
    ItemWaiter,
    OpenhabTmpItem,
    TestBaseRule,
    get_openhab_item_names,
    get_openhab_test_commands,
    get_openhab_test_states,
    get_random_name,
)

import HABApp
from HABApp.openhab.events import ItemCommandEventFilter


class TestOpenhabInterface(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()

        self.add_test('Interface item exists', self.test_item_exists)
        self.add_test('Interface item create/remove', self.test_item_create_delete)
        self.add_test('Interface group create/remove', self.test_item_create_delete_group)
        self.add_test('Interface get item definition', self.test_item_definition)
        self.add_test('Interface change type', self.test_item_change_type)

        # test the states
        for oh_type in get_openhab_item_names():
            self.add_test(
                f'update and commands {oh_type}', self.test_post_update, oh_type,
                get_openhab_test_states(oh_type, only_generic_states=True),
                get_openhab_test_commands(oh_type, only_generic_commands=True)
            )

        # test json post
        self.add_test('post_update (by_json)', self.test_umlaute)
        self.add_test('test_item_not_found', self.test_openhab_item_not_found)
        self.add_test('Interface Metadata', self.test_metadata)
        self.add_test('Test async order', self.test_async_oder)

    def test_item_exists(self) -> None:
        assert not self.openhab.item_exists('item_which_does_not_exist')
        assert self.openhab.item_exists('TestString')

    def test_item_create_delete(self) -> None:
        test_defs = []
        for type in get_openhab_item_names():
            test_defs.append((type, get_random_name(type)))
        # test_defs.append(('Number', 'HABApp_Ping'))

        for item_type, item_name in test_defs:
            assert not self.openhab.item_exists(item_name)

            self.openhab.create_item(item_type, item_name)
            assert self.openhab.item_exists(item_name)

            self.openhab.remove_item(item_name)
            assert not self.openhab.item_exists(item_name)

    def test_item_change_type(self) -> None:
        test_item = get_random_name('String')
        assert not self.openhab.item_exists(test_item)

        self.openhab.create_item('String', test_item)
        assert self.openhab.item_exists(test_item)

        # change item type to number and ensure HABApp picks up correctly on the new type
        self.openhab.create_item('Number', test_item)

        end = time.time() + 2
        while True:
            time.sleep(0.01)
            if time.time() > end:
                HABApp.openhab.items.NumberItem.get_item(test_item)
                break

            if isinstance(HABApp.core.Items.get_item(test_item), HABApp.openhab.items.NumberItem):
                break

        self.openhab.remove_item(test_item)

    def test_item_create_delete_group(self) -> None:
        test_item = get_random_name('String')
        test_group = get_random_name('Group')
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

    def test_post_update(self, oh_type, post_updates, send_commands) -> None:

        with OpenhabTmpItem(oh_type) as item:
            with ItemWaiter(item) as waiter:
                for post_value, receive_value in post_updates:
                    self.openhab.post_update(item, post_value)
                    waiter.wait_for_state(receive_value)
            with EventWaiter(item, ItemCommandEventFilter()) as waiter:
                for post_command, receive_command in send_commands:
                    self.openhab.send_command(item, post_command)
                    waiter.wait_for_event(value=receive_command)

    @OpenhabTmpItem.use('String')
    def test_umlaute(self, item: OpenhabTmpItem) -> None:
        LABEL = 'äöß'

        self.openhab.create_item('String', item.name, label=LABEL)
        ret = self.openhab.get_item(item.name)
        assert ret.label == LABEL, f'"{LABEL}" != "{ret.label}"'

    def test_openhab_item_not_found(self) -> None:
        test_item = get_random_name('String')
        assert self.openhab.get_item(test_item) is None

    def test_item_definition(self) -> None:
        self.openhab.get_item('TestGroupAVG')
        self.openhab.get_item('TestNumber')
        self.openhab.get_item('TestString')

    def test_metadata(self) -> None:
        with OpenhabTmpItem('String') as item:
            self.openhab.set_metadata(item, 'MyNameSpace', 'MyValue', {'key': 'value'})
            self.openhab.remove_metadata(item, 'MyNameSpace')

    def test_async_oder(self) -> None:
        with OpenhabTmpItem('String', 'AsyncOrderTest') as item, ItemWaiter(item) as waiter:
            for _ in range(10):
                for i in range(5):
                    item.oh_post_update(str(i))
            waiter.wait_for_state('4')


TestOpenhabInterface()
