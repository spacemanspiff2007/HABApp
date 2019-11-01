import dataclasses
import logging
import typing

from HABApp.core.items import Item
from HABApp.openhab.items import SwitchItem, RollershutterItem, DimmerItem, ColorItem
from HABAppTests import TestBaseRule, ItemWaiter, OpenhabTmpItem

log = logging.getLogger('HABApp.Test')


@dataclasses.dataclass
class TestParam():
    func_name: str
    result: typing.Union[str, float, int]
    func_param: typing.Union[str, float, int] = None


class TestOpenhabItemFuncs(TestBaseRule):
    """This rule is testing the OpenHAB item types by calling functions and checking values"""

    def __init__(self):
        super().__init__()


        self.add_test('SwitchItem', self.test_item, SwitchItem,
                      [TestParam('on', 'ON'), TestParam('off', 'OFF')])
        self.add_test('RollershutterItem', self.test_item, RollershutterItem,
                      [TestParam('percent', 55.5, 55.5), TestParam('up', 0), TestParam('down', 100)])
        self.add_test('DimmerItem', self.test_item, DimmerItem,
                      [TestParam('percent', 55.5, 55.5), TestParam('on', 100), TestParam('off', 0)])
        self.add_test('ColorItem', self.test_item, ColorItem, [
            TestParam('on', (None, None, 100)),
            TestParam('off', (None, None, 0)),
            TestParam('percent', (None, None, 55.5), 55.5)
        ])

    def test_item(self, item_type, test_params):

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

                # reset state so we don't get false positives
                item.set_value(None)

            test_ok = waiter.states_ok

        return test_ok


TestOpenhabItemFuncs()
