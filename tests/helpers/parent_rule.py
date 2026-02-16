import pytest

import HABApp
import HABApp.core.items.base_item_watch
from HABApp.core.internals import ContextProvidingObj, ExecutorFactory


class DummyRule(ContextProvidingObj):
    def __init__(self, event_bus, item_registry, executor_factory: ExecutorFactory) -> None:
        super().__init__(context=HABApp.rule_ctx.HABAppRuleContext(self, event_bus, item_registry, executor_factory))
        self.rule_name = 'DummyRule'


@pytest.fixture
def parent_rule(monkeypatch, eb, ir, sync_worker):
    rule = DummyRule(eb, ir, sync_worker)

    def ret_dummy_rule_context():
        return rule._habapp_ctx

    # patch imports
    monkeypatch.setattr(HABApp.core.internals, 'get_current_context', ret_dummy_rule_context)
    monkeypatch.setattr(HABApp.core.internals.context.get_context, 'get_current_context', ret_dummy_rule_context)

    monkeypatch.setattr(HABApp.core.items.base_item_watch, 'get_current_context', ret_dummy_rule_context)

    return rule
