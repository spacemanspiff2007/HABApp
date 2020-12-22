from pytest import fixture

import HABApp


class DummyRule:
    def __init__(self):
        self.rule_name = 'DummyRule'

        self.__dict__['_Rule__event_listener'] = []

    def register_cancel_obj(self, obj):
        pass

    # copied funcs
    _get_cb_name = HABApp.Rule._get_cb_name
    _add_event_listener = HABApp.Rule._add_event_listener


@fixture
def parent_rule(monkeypatch):
    rule = DummyRule()

    # patch both imports imports
    monkeypatch.setattr(HABApp.rule,      'get_parent_rule', lambda: rule, raising=True)
    monkeypatch.setattr(HABApp.rule.rule, 'get_parent_rule', lambda: rule, raising=True)

    # util imports
    monkeypatch.setattr(HABApp.util.multimode.item, 'get_parent_rule', lambda: rule, raising=True)

    yield rule
