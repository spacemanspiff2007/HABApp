import asyncio

from immutables import Map

from HABApp.core.const import loop
from HABApp.core.types import HSB, RGB
from HABApp.openhab.interface_async import async_get_items
from HABApp.openhab.items import GroupItem, StringItem, ColorItem
from HABAppTests import OpenhabTmpItem, TestBaseRule, ItemWaiter


class OpenhabItems(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.add_test('ApiDoc', self.test_api)
        self.add_test('MemberTags', self.test_tags)
        self.add_test('MemberGroups', self.test_groups)
        self.add_test('TestExisting', self.test_existing)
        self.add_test('TestColor', self.test_color)

        self.item_number = OpenhabTmpItem('Number')
        self.item_switch = OpenhabTmpItem('Switch')

        self.item_group = OpenhabTmpItem('Group')
        self.item_string = OpenhabTmpItem('String')

    def set_up(self):
        self.item_number.create_item(label='No metadata')

        self.item_switch.create_item()
        self.openhab.set_metadata(
            self.item_switch.name, 'homekit', 'HeatingThresholdTemperature', {'minValue': 0.5, 'maxValue': 20})

        self.item_group.create_item(label='MyGrpValue [%s]', category='text', tags=['DocItem'],
                                    group_function='AND', group_function_params=['VALUE_TRUE', 'VALUE_FALSE'])
        self.item_string.create_item(label='MyStrValue [%s]', category='text', tags=['DocItem'],
                                     groups=[self.item_group.name])

        self.openhab.set_metadata(self.item_string.name, 'ns1', 'v1', {'key11': 'value11', 'key12': 'value12'})
        self.openhab.set_metadata(self.item_string.name, 'ns2', 'v2', {'key2': 'value2'})
        self.openhab.set_metadata(self.item_group.name, 'ns3', 'v3', {})

    def tear_down(self):
        self.item_string.remove()
        self.item_switch.remove()

    def test_existing(self):
        item = StringItem.get_item('TestString')
        assert item.tags == frozenset(['TestTag'])
        assert item.groups == frozenset(['TestGroup'])
        assert list(item.metadata.keys()) == ['meta1']
        assert item.metadata['meta1'].value == 'test'
        assert item.metadata['meta1'].config == Map({'key': 'value'})

    def test_api(self):
        self.openhab.get_item(self.item_string.name)

        self.openhab.get_item(self.item_number.name, all_metadata=True)
        self.openhab.get_item(self.item_string.name, all_metadata=True)
        self.openhab.get_item(self.item_switch.name, all_metadata=True)

        self.openhab.get_item(self.item_group.name, all_metadata=True)
        asyncio.run_coroutine_threadsafe(async_get_items(all_metadata=True), loop).result()

    @OpenhabTmpItem.use('String', arg_name='oh_item')
    def test_tags(self, oh_item: OpenhabTmpItem):
        oh_item.create_item(tags=['tag1', 'tag2'])

        item = StringItem.get_item(oh_item.name)
        assert item.tags == {'tag1', 'tag2'}

        oh_item.modify(tags=['tag1', 'tag4'])
        assert item.tags == {'tag1', 'tag4'}

        oh_item.modify()
        assert item.tags == set()

    @OpenhabTmpItem.use('String', arg_name='oh_item')
    @OpenhabTmpItem.create('Group', 'group1')
    @OpenhabTmpItem.create('Group', 'group2')
    def test_groups(self, oh_item: OpenhabTmpItem):
        grp1 = GroupItem.get_item('group1')
        grp2 = GroupItem.get_item('group2')

        assert grp1.members == ()
        assert grp2.members == ()

        oh_item.create_item(groups=['group1'])

        item = StringItem.get_item(oh_item.name)
        assert item.groups == {'group1'}
        assert grp1.members == (item, )

        oh_item.modify(groups=['group1', 'group2'])
        assert item.groups == {'group1', 'group2'}
        assert grp1.members == (item, )
        assert grp2.members == (item, )

        oh_item.modify()
        assert item.groups == set()
        assert grp1.members == ()
        assert grp2.members == ()

    @OpenhabTmpItem.create('Color', arg_name='oh_item')
    def test_color(self, oh_item: OpenhabTmpItem):
        item = ColorItem.get_item(oh_item.name)

        with ItemWaiter(item) as waiter:
            for cmd in ((350, 99.3, 1.58), (1, 11.2, 1.72)):
                item.oh_send_command(cmd)
                waiter.wait_for_state(cmd)
                waiter.wait_for_attribs(hue=cmd[0], saturation=cmd[1], brightness=cmd[2])

            for cmd, target in ((HSB(1, 13.25, 22.33), HSB(1, 13.25, 22.33)),
                                (RGB(20, 30, 40), HSB(210, 50, 15.69))):
                item.oh_send_command(cmd)
                waiter.wait_for_state(tuple(target))
                waiter.wait_for_attribs(hue=target[0], saturation=target[1], brightness=target[2])


OpenhabItems()
