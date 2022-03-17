from pytest import fixture

import HABApp


class DummyRule:
    def __init__(self):
        self.rule_name = 'DummyRule'
        self._habapp_rule_ctx = HABApp.rule_ctx.HABAppRuleContext(self)


@fixture
def parent_rule(monkeypatch):
    rule = DummyRule()

    def ret_dummy_rule_context(x=None):
        return rule._habapp_rule_ctx

    # patch both imports imports
    monkeypatch.setattr(HABApp.core.internals, 'get_current_context', ret_dummy_rule_context)
    monkeypatch.setattr(HABApp.core.internals.context.get_context, 'get_current_context', ret_dummy_rule_context)

    yield rule
