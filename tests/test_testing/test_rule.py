import pytest
from whenever import Instant, seconds

from HABApp import Rule
from HABApp.core.events import ItemNoChangeEvent, ItemNoUpdateEvent
from HABApp.core.items import Item
from HABApp.core.provider import HabAppObjProvider
from HABApp.mqtt.items import MqttItem
from HABApp.openhab.definitions.websockets.item_events import ItemCommandEvent
from HABApp.openhab.items import NumberItem, SwitchItem
from HABApp.testing import TestingStartTimeOptions, UserTimeControl
from HABApp.testing.conftest import *  # noqa: F403
from HABApp.testing.items import TestingItems


class TimestampRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        # This item was created by another rule, that's why "get_item" is used
        self.my_item = Item.get_item('Item_Name')

        # There are also functions available which support both building the delta directly and using an object
        if self.my_item.last_change.newer_than(minutes=2, seconds=30):
            print('Item was changed in the last 2min 30s')
        if self.my_item.last_change.older_than(seconds(30)):
            print('Item was changed before 30s')


@pytest.fixture
def testing_start_time() -> TestingStartTimeOptions:
    return TestingStartTimeOptions(start=Instant.from_utc(2024, 4, 30, 10, 32))


async def test_timestamp_rule(capsys, habapp_provider: HabAppObjProvider, time_control: UserTimeControl, rule_hook) -> None:

    item = Item.get_create_item('Item_Name', initial_value='value')
    item._last_change.instant = Instant.from_utc(2024, 4, 30, 10, 30)
    item._last_update.instant = Instant.from_utc(2024, 4, 30, 10, 31)

    TimestampRule()

    assert capsys.readouterr().out == (
        'Item was changed in the last 2min 30s\n'
        'Item was changed before 30s\n'
    )


class SchedulerRule(Rule):
    @staticmethod
    def print(text: str) -> None:
        # cut away the utc timezone information
        print(str(Instant.now().to_tz('utc')).split('+')[0], text)

    def __init__(self) -> None:
        super().__init__()
        self.run.soon(self.print, 'soon')
        self.run.once(1, self.print, 1)
        self.run.once(2, self.print, 2)


async def test_scheduler_rule(capsys, time_control: UserTimeControl, rule_hook) -> None:

    SchedulerRule()

    await time_control.advance(5)

    assert capsys.readouterr().out == (
        '2024-04-30T10:32:00 soon\n'
        '2024-04-30T10:32:01 1\n'
        '2024-04-30T10:32:02 2\n'
    )


class ItemConstRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        item = Item.get_create_item('test_item', initial_value=None)
        item.watch_update(2).listen_event(self.event)
        item.watch_change(5).listen_event(self.event)
        item.post_value(1)

    def event(self, event: ItemNoUpdateEvent | ItemNoChangeEvent) -> None:
        print(
            str(Instant.now().to_tz('utc')).split('+')[0], event
        )


async def test_item_const_rule(capsys, time_control: UserTimeControl, rule_hook, eb) -> None:

    ItemConstRule()

    await time_control.advance(6)

    assert capsys.readouterr().out == (
        '2024-04-30T10:32:02 <ItemNoUpdateEvent name: test_item, seconds: 2.0>\n'
        '2024-04-30T10:32:05 <ItemNoChangeEvent name: test_item, seconds: 5.0>\n'
    )


@pytest.fixture
def testing_items() -> TestingItems:
    return TestingItems().add(SwitchItem, 'test_sw_item', value='OFF').add(NumberItem, 'test_nr_item')


class OhItemRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        self.item = SwitchItem.get_item('test_sw_item')
        assert self.item.is_off()
        self.item.listen_event(self.event, )
        self.item.command_value('ON')

        self.nr_item = NumberItem.get_item('test_nr_item')
        self.nr_item.listen_event(self.event)
        self.nr_item.oh_send_command(10)
        self.nr_item.oh_send_command('15 kWh')

        self.run.soon(self.check_item)

    def event(self, event: ItemCommandEvent) -> None:
        print(
            str(Instant.now().to_tz('utc')).split('+')[0], event
        )

    def check_item(self) -> None:
        assert self.item.is_on()
        assert self.nr_item == 15
        print(str(Instant.now().to_tz('utc')).split('+')[0], 'Items Ok')


async def test_oh_item_rule(capsys, time_control: UserTimeControl, rule_hook, eb) -> None:

    OhItemRule()

    assert capsys.readouterr().out == (
        '2024-04-30T10:32:00 <ItemCommandEvent name: test_sw_item, value: ON>\n'
        '2024-04-30T10:32:00 <ItemStateEvent name: test_sw_item, value: ON>\n'
        '2024-04-30T10:32:00 <ItemStateChangedEvent name: test_sw_item, value: ON, old_value: OFF>\n'

        '2024-04-30T10:32:00 <ItemCommandEvent name: test_nr_item, value: 10>\n'
        '2024-04-30T10:32:00 <ItemStateEvent name: test_nr_item, value: 10>\n'
        '2024-04-30T10:32:00 <ItemStateChangedEvent name: test_nr_item, value: 10, old_value: None>\n'

        '2024-04-30T10:32:00 <ItemCommandEvent name: test_nr_item, value: 15 kWh>\n'
        '2024-04-30T10:32:00 <ItemStateEvent name: test_nr_item, value: 15 kWh>\n'
        '2024-04-30T10:32:00 <ItemStateChangedEvent name: test_nr_item, value: 15 kWh, old_value: 10>\n'

        '2024-04-30T10:32:00 Items Ok\n'
    )


class MqttItemRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        self.item = MqttItem.get_create_item('my/topic')
        self.item.listen_event(self.event)
        self.item.publish(123)

        self.run.soon(self.check_item)

    def event(self, event: ItemCommandEvent) -> None:
        print(
            str(Instant.now().to_tz('utc')).split('+')[0], event
        )

    def check_item(self) -> None:
        assert self.item == 123
        print(str(Instant.now().to_tz('utc')).split('+')[0], 'Items Ok')


async def test_mqtt_item_rule(capsys, time_control: UserTimeControl, rule_hook, eb) -> None:

    MqttItemRule()

    assert capsys.readouterr().out == (
        '2024-04-30T10:32:00 <MqttValueUpdateEvent name: my/topic, value: 123>\n'
        '2024-04-30T10:32:00 <MqttValueChangeEvent name: my/topic, value: 123, old_value: None>\n'

        '2024-04-30T10:32:00 Items Ok\n'
    )
