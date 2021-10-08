from HABApp.openhab.items import StringItem, GroupItem
from HABAppTests import TestBaseRule, OpenhabTmpItem


class OpenhabItems(TestBaseRule):

    def __init__(self):
        super().__init__()

        self.add_test('ApiDoc', self.test_api)
        self.add_test('MemberTags', self.test_tags)
        self.add_test('MemberGroups', self.test_groups)

    def test_api(self):
        with OpenhabTmpItem('String') as item:
            self.openhab.get_item(item.name)

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
