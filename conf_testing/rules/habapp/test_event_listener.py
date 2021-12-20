import logging

from HABApp.core.events import ValueChangeEvent
from HABApp.core.items import Item
from HABApp.util import EventListenerGroup
from HABAppTests import TestBaseRule, get_random_name

log = logging.getLogger('HABApp.Tests.MultiMode')


class TestWarningOnRuleUnload(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self):
        super().__init__()

        self.add_test('CheckWarning', self.test_unload)

    def test_unload(self):
        item = Item.get_create_item(get_random_name('HABApp'))

        grp = EventListenerGroup().add_listener(item, self.cb, ValueChangeEvent)

        for _ in range(20):
            grp.listen()
            grp.cancel()

        self._habapp_rule_ctx.unload_rule()

    def cb(self, event):
        pass


# TestWarningOnRuleUnload()
