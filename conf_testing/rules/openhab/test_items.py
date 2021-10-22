import asyncio

from HABApp.core.const import loop
from HABApp.openhab.interface_async import async_get_items
from HABApp.openhab.items import GroupItem, StringItem
from HABAppTests import OpenhabTmpItem, TestBaseRule


class OpenhabItems(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.add_test('ApiDoc', self.test_api)
        self.add_test('MemberTags', self.test_tags)
        self.add_test('MemberGroups', self.test_groups)

        self.item_group = OpenhabTmpItem('Group')
        self.item_string = OpenhabTmpItem('String')
        self.item_switch = OpenhabTmpItem('Switch')

    def set_up(self):
        self.item_switch.create_item()
        self.item_group.create_item(label='MyGrpValue [%s]', category='text', tags=['DocItem'],
                                    group_function='AND', group_function_params=['VALUE_TRUE', 'VALUE_FALSE'])
        self.item_string.create_item(label='MyStrValue [%s]', category='text', tags=['DocItem'],
                                     groups=[self.item_group.name])

        self.openhab.set_metadata(self.item_string.name, 'ns1', 'v1', {'key11': 'value11', 'key12': 'value12'})
        self.openhab.set_metadata(self.item_string.name, 'ns2', 'v2', {'key2': 'value2'})
        self.openhab.set_metadata(self.item_group.name, 'ns3', 'v3', {})
        self.openhab.set_metadata(
            self.item_switch.name, 'homekit', 'HeatingThresholdTemperature', {'minValue': 0.5, 'maxValue': 20})

    def tear_down(self):
        self.item_string.remove()
        self.item_switch.remove()

    def test_api(self):
        self.openhab.get_item(self.item_string.name)
        self.openhab.get_item(self.item_string.name, metadata='.*')
        self.openhab.get_item(self.item_switch.name, metadata='.*')
        self.openhab.get_item(self.item_group.name, metadata='.*')
        asyncio.run_coroutine_threadsafe(async_get_items(metadata='.*'), loop).result()

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

        assert grp1.members == tuple()
        assert grp2.members == tuple()

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
        assert grp1.members == tuple()
        assert grp2.members == tuple()


OpenhabItems()
