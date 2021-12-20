from pytest import fixture

import HABApp


class DummyRule:
    def __init__(self):
        self.rule_name = 'DummyRule'
        self._habapp_rule_ctx = HABApp.rule_ctx.HABAppRuleContext(self)

        self.__dict__['_Rule__event_listener'] = []


@fixture
def parent_rule(monkeypatch):
    rule = DummyRule()

    def ret_dummy_rule_context(x=None):
        return rule._habapp_rule_ctx

    # patch both imports imports
    monkeypatch.setattr(HABApp.rule_ctx, 'get_rule_context', ret_dummy_rule_context, raising=True)

    # util imports
    monkeypatch.setattr(HABApp.util.multimode.item, 'get_rule_context', ret_dummy_rule_context, raising=True)

    yield rule
