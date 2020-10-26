from HABAppTests import ItemWaiter, OpenhabTmpItem, TestBaseRule, get_random_name

import HABApp
import logging
from HABApp.openhab.items import OpenhabItem
from HABApp.util.multimode import MultiModeItem, SwitchItemValueMode

log = logging.getLogger('HABApp.Tests.MultiMode')



class TestSwitchMode(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self):
        super().__init__()

        self.add_test('SwitchItemValueMode', self.test_sw_mode)
        self.add_test('SwitchItemValueMode inverted', self.test_sw_mode_inverted)

    def test_sw_mode(self):
        mm = MultiModeItem.get_create_item(get_random_name())

        with OpenhabTmpItem(None, 'Switch') as switch, ItemWaiter(OpenhabItem.get_item(switch.name)) as waiter:
            switch.on()
            waiter.wait_for_state('ON')

            mode = SwitchItemValueMode('test', switch)
            mm.add_mode(0, mode)

            assert mode.enabled is True, mode.enabled

            switch.off()
            waiter.wait_for_state('OFF')
            assert switch.is_off()
            assert mode.enabled is False, mode.enabled

            mode.set_value('asdf')
            assert mode.enabled is False, mode.enabled

            mode.set_value(0)
            assert mode.enabled is False, mode.enabled

        HABApp.core.Items.pop_item(mm.name)

    def test_sw_mode_inverted(self):
        mm = MultiModeItem.get_create_item(get_random_name())

        with OpenhabTmpItem(None, 'Switch') as switch, ItemWaiter(OpenhabItem.get_item(switch.name)) as waiter:
            switch.on()
            waiter.wait_for_state('ON')

            mode = SwitchItemValueMode('test', switch, invert_switch=True, logger=log)
            mm.add_mode(0, mode)
            assert mode.enabled is False, mode.enabled

            mode.set_value('asdf')
            assert mode.enabled is False, mode.enabled

            mode.set_value(0)
            assert mode.enabled is False, mode.enabled

            switch.off()
            waiter.wait_for_state('OFF')
            assert mode.enabled is True, mode.enabled

        HABApp.core.Items.pop_item(mm.name)


TestSwitchMode()
