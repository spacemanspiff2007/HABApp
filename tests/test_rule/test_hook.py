import logging

import pytest

from HABApp.rule.rule_hook import HABAppRuleHook


def test_rule_hook_log(caplog) -> None:

    class MyRule:
        pass

    rules = []
    hook = HABAppRuleHook(rules.append, lambda x: x.__class__.__name__, None, None)
    with hook:
        hook.register_rule(MyRule())

    assert caplog.records == []

    hook.register_rule(MyRule())
    assert caplog.record_tuples == [
        ('HABApp.Rule', logging.WARNING, 'Added another rule of type MyRule but file load has already been completed!')
    ]
    caplog.records.clear()


def test_rule_hook_exception():

    rules = []
    hook = HABAppRuleHook(rules.append, lambda x: x.__class__.__name__, None, None)

    with pytest.raises(ValueError):
        with hook:
            raise ValueError()
