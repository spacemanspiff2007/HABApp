from HABApp.openhab.items import StringItem
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
        oh_item.create(tags=['tag1', 'tag2'])

        item = StringItem.get_item(oh_item.name)
        assert item.tags == ('tag1', 'tag2')

        oh_item.modify(tags=['tag1', 'tag4'])
        assert item.tags == ('tag1', 'tag4')

        oh_item.modify()
        assert item.tags == tuple()

    @OpenhabTmpItem.use('String', arg_name='oh_item')
    def test_groups(self, oh_item: OpenhabTmpItem):
        oh_item.create(groups=['group1'])

        item = StringItem.get_item(oh_item.name)
        assert item.groups == ('group1', )

        oh_item.modify(groups=['group1', 'group2'])
        assert item.groups == ('group1', 'group2')

        oh_item.modify()
        assert item.groups == tuple()


OpenhabItems()
