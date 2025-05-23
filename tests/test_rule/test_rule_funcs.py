from unittest.mock import MagicMock

import pytest

from HABApp import Rule
from tests.helpers import TestEventBus
from tests.rule_runner import ErrorEventReceivedError, SimpleRuleRunner


@pytest.mark.no_internals
async def test_unload_function() -> None:

    async with SimpleRuleRunner():
        r = Rule()
        m = MagicMock()
        r.on_rule_removed = m
        assert not m.called

    assert m.called


@pytest.mark.ignore_log_errors
@pytest.mark.no_internals
async def test_unload_function_exception(eb: TestEventBus) -> None:
    eb.allow_errors = True

    try:
        async with SimpleRuleRunner():
            r = Rule()
            m = MagicMock(side_effect=ValueError)
            r.on_rule_removed = m
            assert not m.called
    except ErrorEventReceivedError:
        pass

    assert m.called


@pytest.mark.no_internals
async def test_repr() -> None:
    class Abc(Rule):
        def __init__(self) -> None:
            super().__init__()
            self.rule_name = 'Abc'

    async with SimpleRuleRunner():
        rule = Abc()
        assert repr(rule) == '<Abc>'

        rule.rule_name = 'MyName'
        assert repr(rule) == '<Abc MyName>'
