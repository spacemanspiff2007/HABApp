from typing import Final

from HABAppTests import TestBaseRule, get_random_name

from HABApp.core.events import ValueChangeEventFilter
from HABApp.core.items import Item
from HABApp.rule_ctx import HABAppRuleContext
from HABApp.util import EventListenerGroup


class TestNoWarningOnRuleUnload(TestBaseRule):
    """This rule tests that multiple listen/cancel commands don't create warnings on unload"""

    def __init__(self) -> None:
        super().__init__()

        self.add_test('CheckWarning', self.test_unload)

    async def test_unload(self) -> None:

        item = Item.get_create_item(get_random_name('HABApp'))

        grp = EventListenerGroup().add_listener(item, self.cb, ValueChangeEventFilter())

        for _ in range(20):
            grp.listen()
            grp.cancel()

        # _habapp_ctx gets set None during unload so we remember the context here
        ctx: Final = self._habapp_ctx

        await self._habapp_ctx.unload_rule()

        # Workaround to so we don't crash
        self.on_rule_unload = lambda: None
        self._habapp_ctx = HABAppRuleContext(self, ctx.event_bus, ctx.item_registry, ctx.executor_factory)

    def cb(self, event) -> None:
        pass


TestNoWarningOnRuleUnload()
