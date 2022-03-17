from pytest import fixture

import HABApp
import HABApp.core.items.base_item_watch
from HABApp.core.internals import ContextMixin


class DummyRule(ContextMixin):
    def __init__(self):
        super().__init__(context=HABApp.rule_ctx.HABAppRuleContext(self))
        self.rule_name = 'DummyRule'


@fixture
def parent_rule(monkeypatch):
    rule = DummyRule()

    def ret_dummy_rule_context():
        return rule._habapp_ctx

    # patch imports
    monkeypatch.setattr(HABApp.core.internals, 'get_current_context', ret_dummy_rule_context)
    monkeypatch.setattr(HABApp.core.internals.context.get_context, 'get_current_context', ret_dummy_rule_context)

    monkeypatch.setattr(HABApp.core.items.base_item_watch, 'get_current_context', ret_dummy_rule_context)

    yield rule
