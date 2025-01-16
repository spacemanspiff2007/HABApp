import dataclasses
import logging

from HABAppTests import (
    ItemWaiter,
    OpenhabTmpItem,
    TestBaseRule,
)

from HABApp.core.types import HSB
from HABApp.openhab.items import (
    ColorItem,
    ContactItem,
    DimmerItem,
    NumberItem,
    OpenhabItem,
    RollershutterItem,
    SwitchItem,
)


log = logging.getLogger('HABApp.Tests')


@dataclasses.dataclass(frozen=True)
class TestParam:
    func_name: str
    result: str | float | int | tuple | HSB
    func_params: str | float | int | tuple = None


class TestOpenhabItemFuncs(TestBaseRule):
    """This rule is testing the OpenHAB item types by calling functions and checking values"""

    def __init__(self) -> None:
        super().__init__()

        self.add_func_test(ContactItem, {TestParam('open', 'OPEN'), TestParam('closed', 'CLOSED')})

        p_on = {TestParam('on', 'ON'), TestParam('off', 'OFF')}
        p_int = {TestParam('percent', 50, 50), TestParam('percent', 100, 100), TestParam('percent', 0, 0)}
        p_float = {
            TestParam('percent', 55.5, 55.5), TestParam('percent', 100.0, 100.0), TestParam('percent', 0.0, 0.0),
        }

        self.add_func_test(SwitchItem, p_on)

        self.add_func_test(
            RollershutterItem, {TestParam('up', 0), TestParam('down', 100)} | p_int | p_float
        )

        self.add_func_test(
            DimmerItem, {TestParam('on', 100), TestParam('off', 0)} | p_int | p_float
        )

        self.add_func_test(
            ColorItem, [
                TestParam('on', HSB(0, 0, 100)),
                TestParam('off', HSB(0, 0, 0)),
                TestParam('percent', func_params=55.5, result=HSB(0, 0, 55.5))
            ]
        )

    def add_func_test(self, cls, params: set | list) -> None:
        # <class 'HABApp.openhab.items.switch_item.SwitchItem'> -> SwitchItem
        self.add_test(cls.__name__, self.test_func, cls, params)

    def test_func(self, item_type, test_params) -> None:

        # create a nice name for the tmp item
        item_type = str(item_type).split('.')[-1][:-6]
        item_name = f'{item_type}_item_test'

        with OpenhabTmpItem(item_type, item_name) as item, ItemWaiter(OpenhabItem.get_item(item_name)) as waiter:
            for test_param in test_params:
                assert isinstance(test_param, TestParam)

                func = getattr(item, test_param.func_name)
                if test_param.func_params is None:
                    func()
                else:
                    if isinstance(test_param.func_params, (str, float, int, bytes)):
                        func(test_param.func_params)
                    else:
                        func(*test_param.func_params)

                if waiter.wait_for_state(test_param.result):
                    log.info(f'{item_type}.{test_param.func_name}() is ok!')

                # test properties
                if test_param.func_name not in ('percent', 'oh_post_update', 'oh_send_command'):
                    prop_name = f'is_{test_param.func_name}'
                    assert getattr(item, prop_name)() is True
                    log.info(f'{item_type}.{prop_name}() is ok!')

                # reset state so we don't get false positives
                item.set_value(None)


TestOpenhabItemFuncs()


class TestOpenhabItemConvenience(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()
        self.add_test('post_value_if', self.test_post_update_if)

    @OpenhabTmpItem.create('Number', arg_name='oh_item')
    def test_post_update_if(self, oh_item: OpenhabTmpItem) -> None:
        item = NumberItem.get_item(oh_item.name)

        with ItemWaiter(OpenhabItem.get_item(item.name)) as waiter:
            item.post_value_if(0, is_=None)
            waiter.wait_for_state(0)

            item.post_value_if(1, eq=0)
            waiter.wait_for_state(1)

            item.post_value_if(5, lower_equal=1)
            waiter.wait_for_state(5)


TestOpenhabItemConvenience()
