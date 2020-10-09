from pytest import fixture

import HABApp


class DummyRule:
    def __init__(self):
        self.rule_name = 'DummyRule'

    def register_cancel_obj(self, obj):
        pass


@fixture
def parent_rule(monkeypatch):
    rule = DummyRule()
    # beide imports
    monkeypatch.setattr(HABApp.rule,      'get_parent_rule', lambda: rule, raising=True)
    monkeypatch.setattr(HABApp.rule.rule, 'get_parent_rule', lambda: rule, raising=True)

    # util imports
    monkeypatch.setattr(HABApp.util.multimode.item, 'get_parent_rule', lambda: rule, raising=True)

    yield rule
