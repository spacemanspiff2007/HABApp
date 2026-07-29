from typing import Final

import whenever
from HABAppTests import EventWaiter, ItemWaiter, OpenhabTmpItem, TestBaseRule
from immutables import Map

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.openhab.connection.handler import OpenHabAsyncInterface
from HABApp.openhab.items import GroupItem, NumberItem, StringItem


class OpenhabItems(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()

        self.add_test('Api', self.test_api)
        self.add_test('AsyncApi', self.test_api_async)
        self.add_test('MemberTags', self.test_tags)
        self.add_test('MemberGroups', self.test_groups)
        self.add_test('TestExisting', self.test_existing)
        self.add_test('TestGroupFunction', self.test_group_func)

        self.add_test('TestSmallValues', self.test_small_float_values)
        self.add_test('TestLastValue', self.test_last_value)
        self.add_test('TestOhTimestamp', self.test_oh_timestamp)

        self.item_number = OpenhabTmpItem('Number')
        self.item_switch = OpenhabTmpItem('Switch')

        self.item_group = OpenhabTmpItem('Group')
        self.item_string = OpenhabTmpItem('String')

    def set_up(self) -> None:
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

    def tear_down(self) -> None:
        self.item_string.remove()
        self.item_switch.remove()

    def test_existing(self) -> None:
        item = StringItem.get_item('TestString')
        assert item.tags == frozenset(['TestTag'])
        assert item.groups == frozenset(['TestGroup'])
        assert list(item.metadata.keys()) == ['meta1']
        assert item.metadata['meta1'].value == 'test'
        assert item.metadata['meta1'].config == Map({'key': 'value'})

    def test_api(self) -> None:
        self.openhab.get_item(self.item_string.name)

        self.openhab.get_item(self.item_number.name)
        self.openhab.get_item(self.item_string.name)
        self.openhab.get_item(self.item_switch.name)

        self.openhab.get_item(self.item_group.name)

    async def test_api_async(self) -> None:
        await HABAPP_PROVIDER.get_existing(OpenHabAsyncInterface).get_items()

    def test_small_float_values(self) -> None:
        # https://github.com/spacemanspiff2007/HABApp/issues/425
        with OpenhabTmpItem('Number') as item:
            assert item.value is None
            for i in range(3, 19, 3):
                with ItemWaiter(item) as waiter:
                    value = 1 / 10 ** i
                    item.oh_post_update(value)
                    waiter.wait_for_state(value)

        # https://github.com/spacemanspiff2007/HABApp/issues/485
        with OpenhabTmpItem('Number:Length') as item:
            assert item.value is None
            for i in range(3, 19, 3):
                with ItemWaiter(item) as waiter:
                    value = 1 / 10 ** i
                    item.oh_post_update(f'{value} m')
                    waiter.wait_for_state(value)

    @OpenhabTmpItem.use('String', arg_name='oh_item')
    def test_tags(self, oh_item: OpenhabTmpItem) -> None:
        oh_item.create_item(tags=['tag1', 'tag2'])

        item = StringItem.get_item(oh_item.name)
        assert item.tags == {'tag1', 'tag2'}

        oh_item.modify(tags=['tag1', 'tag4'])
        assert item.tags == {'tag1', 'tag4'}

        oh_item.modify()
        assert item.tags == set()

    @OpenhabTmpItem.use('String', arg_name='oh_item1')
    @OpenhabTmpItem.use('String', arg_name='oh_item2')
    @OpenhabTmpItem.create('Group', 'group1')
    @OpenhabTmpItem.create('Group', 'group2')
    def test_groups(self, oh_item1: OpenhabTmpItem, oh_item2: OpenhabTmpItem) -> None:
        grp1 = GroupItem.get_item('group1')
        grp2 = GroupItem.get_item('group2')

        assert grp1.members == ()
        assert grp2.members == ()

        oh_item1.create_item(groups=['group1'])

        item1 = StringItem.get_item(oh_item1.name)
        assert item1.groups == {'group1'}
        assert grp1.members == (item1, )

        oh_item1.modify(groups=['group1', 'group2'])
        assert item1.groups == {'group1', 'group2'}
        assert grp1.members == (item1, )
        assert grp2.members == (item1, )

        oh_item2.create_item(groups=['group1'])

        item2 = StringItem.get_item(oh_item2.name)
        assert item2.groups == {'group1', }
        assert grp1.members == (item1, item2)
        assert grp2.members == (item1, )

        oh_item2.modify()
        assert item2.groups == set()
        assert grp1.members == (item1, )
        assert grp2.members == (item1, )

        oh_item1.modify()
        assert item1.groups == set()
        assert grp1.members == ()
        assert grp2.members == ()

    @OpenhabTmpItem.use('Switch', arg_name='sw1')
    @OpenhabTmpItem.use('Switch', arg_name='sw2')
    @OpenhabTmpItem.use('Group', arg_name='grp')
    def test_group_func(self, sw1: OpenhabTmpItem, sw2: OpenhabTmpItem, grp: OpenhabTmpItem) -> None:
        grp_item = grp.create_item(group_type='Switch', group_function='AND', group_function_params=['ON', 'OFF'])

        sw1_item = sw1.create_item(groups=[grp_item.name])
        sw2_item = sw2.create_item(groups=[grp_item.name])

        with EventWaiter(grp_item.name, ValueUpdateEventFilter(value='ON')) as e:
            sw1_item.oh_send_command('ON')
            sw2_item.oh_send_command('ON')
            e.wait_for_event()

        assert grp_item.value == 'ON'

        with EventWaiter(grp_item.name, ValueUpdateEventFilter(value='OFF')) as e:
            sw1_item.oh_send_command('OFF')
            e.wait_for_event()

        assert grp_item.value == 'OFF'

    @OpenhabTmpItem.create('Number', arg_name='tmp_item')
    def test_last_value(self, tmp_item: OpenhabTmpItem) -> None:
        item = NumberItem.get_item(tmp_item.name)

        with EventWaiter(item.name, ValueUpdateEventFilter()) as e:

            def _send_and_check(value: int | None, last_value: int | None) -> None:
                item.oh_post_update(value)
                e.wait_for_event()
                assert item.value == value
                assert item.last_value == last_value

            for _ in range(3):
                _send_and_check(1, None)

            for _ in range(3):
                _send_and_check(2, 1)

            for _ in range(3):
                _send_and_check(None, 2)

            for _ in range(3):
                _send_and_check(3, None)

    @OpenhabTmpItem.create('Number', arg_name='tmp_item')
    def test_oh_timestamp(self, tmp_item: OpenhabTmpItem) -> None:
        """This rule tests that the timestamp from openHAB is used to set the item time"""
        item = NumberItem.get_item(tmp_item.name)

        # we need a value, if we update from NULL the timestamps are missing
        item.oh_post_update(0)
        with ItemWaiter(item) as w:
            w.wait_for_state(0)

        # openHAB timestamps are ~20ms off so we have to round
        ts_now: Final = whenever.Instant.now().round(
            unit='millisecond', increment=10, mode='floor').subtract(milliseconds=10)
        ts_past: Final = ts_now.subtract(hours=1)

        with whenever.patch_current_time(ts_past, keep_ticking=False):
            item.post_value(1)
            assert item.last_update._instant == ts_past
            assert item.last_change._instant == ts_past

            item.oh_post_update(2)
            with ItemWaiter(item) as w:
                w.wait_for_state(2)

            assert item.last_update._instant > ts_now
            assert item.last_change._instant > ts_now


OpenhabItems()
