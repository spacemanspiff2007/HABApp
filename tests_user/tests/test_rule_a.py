# ruff: noqa: S101, PLR2004
import pytest
from whenever import TimeDelta

from HABApp.openhab.items import NumberItem, StringItem
from HABApp.testing import TestingItems, UserTimeControl
from tests_user.rules.rule_a import RuleA


@pytest.fixture
def testing_items() -> TestingItems:
    items = TestingItems()
    items.add('Number', 'nr_test_item')
    items.add('String', 'str_test_item')
    return items


@pytest.fixture
def rule_a(testing_rules) -> RuleA:
    return RuleA('test_item')


async def test_nr_item_part(rule_a: RuleA, time_control: UserTimeControl) -> None:
    nr = NumberItem.get_item('nr_test_item')
    nr.oh_post_update(0)

    await time_control.advance(60)

    assert nr.value == 1

    await time_control.advance(TimeDelta(minutes=2))

    assert nr.value == 3


async def test_str_item_part(rule_a: RuleA, time_control: UserTimeControl, capsys) -> None:
    str_item = StringItem.get_item('str_test_item')
    str_item.oh_post_update('Initial')

    assert str_item.value == 'Initial'

    str_item.oh_send_command('Change')
    assert str_item.value == 'Change'

    # this is needed because it is an async function
    await time_control.sleep()

    assert str_item.value == 'Updated Change'
