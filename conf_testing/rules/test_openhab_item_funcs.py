import dataclasses
import logging
import typing

from HABApp.core.items import Item
from HABApp.openhab.items import SwitchItem, RollershutterItem, DimmerItem, ColorItem
from HABAppTests import TestBaseRule, ItemWaiter, OpenhabTmpItem

log = logging.getLogger('HABApp.Tests')


@dataclasses.dataclass
class TestParam():
    func_name: str
    result: typing.Union[str, float, int]
    func_param: typing.Union[str, float, int] = None


class TestOpenhabItemFuncs(TestBaseRule):
    """This rule is testing the OpenHAB item types by calling functions and checking values"""

    def __init__(self):
        super().__init__()

        self.add_func_test(
            SwitchItem, [TestParam('on', 'ON'), TestParam('off', 'OFF')]
        )

        self.add_func_test(
            RollershutterItem, [TestParam('percent', 55.5, 55.5), TestParam('up', 0), TestParam('down', 100)]
        )

        self.add_func_test(
            DimmerItem, [TestParam('percent', 55.5, 55.5), TestParam('on', 100), TestParam('off', 0)]
        )

        self.add_func_test(
            ColorItem, [
                TestParam('on', (None, None, 100)),
                TestParam('off', (None, None, 0)),
                TestParam('percent', func_param=55.5, result=(None, None, 55.5))
            ]
        )


    def add_func_test(self, cls, params: list):
        # <class 'HABApp.openhab.items.switch_item.SwitchItem'> -> SwitchItem
        self.add_test(str(cls).split('.')[-1][:-2], self.test_func, cls, params)


    def test_func(self, item_type, test_params):

        # create a nice name for the tmp item
        item_type = str(item_type).split('.')[-1][:-6]
        item_name = f'{item_type}_item_test'

        with OpenhabTmpItem(item_name, item_type) as item, ItemWaiter(Item.get_item(item_name)) as waiter:
            for test_param in test_params:
                assert isinstance(test_param, TestParam)

                if test_param.func_param is None:
                    getattr(item, test_param.func_name)()
                else:
                    getattr(item, test_param.func_name)(test_param.func_param)

                if waiter.wait_for_state(test_param.result):
                    log.info(f'{item_type}.{test_param.func_name}() is ok!')

                if test_param.func_name != 'percent':
                    prop_name = f'is_{test_param.func_name}'
                    assert getattr(item, prop_name)() is True
                    log.info(f'{item_type}.{prop_name}() is ok!')

                # reset state so we don't get false positives
                item.set_value(None)

            test_ok = waiter.states_ok

        return test_ok


a = TestOpenhabItemFuncs()
