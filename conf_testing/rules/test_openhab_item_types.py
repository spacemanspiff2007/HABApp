import dataclasses
import logging
import time

import HABApp
from HABApp.openhab.items import SwitchItem, RollershutterItem, DimmerItem

log = logging.getLogger('HABApp.OpenhabTestItems')


@dataclasses.dataclass
class TestParam():
    func_name: str
    result: str
    func_param: str = None


class TestOpenhabItemTypes(HABApp.Rule):
    """This rule is testing the OpenHAB item types by calling functions and checking values"""

    def __init__(self):
        super().__init__()

        self.values = {}
        self.values_get = {}

        self.tests = {
            SwitchItem: [TestParam('on', 'ON'), TestParam('off', 'OFF')],
            RollershutterItem: [TestParam('percent', 55.5, 55.5), TestParam('up', 0), TestParam('down', 100)],
            DimmerItem: [TestParam('percent', 55.5, 55.5), TestParam('on', 100), TestParam('off', 0)],
        }

        self.run_soon(self.run_tests)

    def run_tests(self):

        assert self.openhab.item_exists('this_item_does_not_exist!') is False

        for item_cls, test_params in self.tests.items():

            item_type = str(item_cls).split('.')[-1][:-6]
            item_name = f'{item_type}_item_test'

            assert self.openhab.item_exists(item_name) is False
            self.openhab.create_item(item_type, item_name)
            assert self.openhab.item_exists(item_name) is True

            start = time.time()
            timeout = False

            while not self.item_exists(item_name) and not timeout:
                time.sleep(0.01)
                if time.time() > start + 1:
                    timeout = True

            if timeout:
                log.error(f'Timeout testing {item_name}')
                continue

            for test_param in test_params:
                assert isinstance(test_param, TestParam)

                start = time.time()
                timeout = False

                item = self.get_item(item_name)
                if test_param.func_param is None:
                    getattr(item, test_param.func_name)()
                else:
                    getattr(item, test_param.func_name)(test_param.func_param)

                while not item.state == test_param.result and not timeout:
                    time.sleep(0.01)
                    if time.time() > start + 1:
                        timeout = True

                if timeout:
                    log.error(f'Timeout testing {item_type}.{test_param.func_name}')
                    continue

                log.info(f'{item_type}.{test_param.func_name}() is ok!')

                # reset state so we don't get false positives
                item.state = None

            self.openhab.remove_item( item_name)


TestOpenhabItemTypes()
