import logging

from HABAppTests import TestBaseRule, get_random_name

from HABApp.core.events import ValueChangeEventFilter
from HABApp.core.items import Item
from HABApp.rule_ctx import HABAppRuleContext
from HABApp.util import EventListenerGroup


log = logging.getLogger('HABApp.Tests.MultiMode')


class TestNoWarningOnRuleUnload(TestBaseRule):
    """This rule tests that multiple listen/cancel commands don't create warnings on unload"""

    def __init__(self):
        super().__init__()

        self.add_test('CheckWarning', self.test_unload)

    def test_unload(self):
        item = Item.get_create_item(get_random_name('HABApp'))

        grp = EventListenerGroup().add_listener(item, self.cb, ValueChangeEventFilter())

        for _ in range(20):
            grp.listen()
            grp.cancel()

        self._habapp_ctx.unload_rule()

        # workaround so we don't get Errors
        for k in ['_TestBaseRule__sub_warning', '_TestBaseRule__sub_errors']:
            obj = self.__dict__[k]
            self.__dict__[k] = None
            assert obj._parent_ctx is None

        # Workaround to so we don't crash
        self.on_rule_unload = lambda: None
        self._habapp_ctx = HABAppRuleContext(self)

    def cb(self, event):
        pass


TestNoWarningOnRuleUnload()
