import unittest
from unittest.mock import MagicMock

from HABApp import Rule
from ..rule_runner import SimpleRuleRunner


def test_unload_function():

    with SimpleRuleRunner():
        r = Rule()
        m = MagicMock()
        assert not m.called
        r.register_on_unload(m)
    assert m.called


def test_unload_function_exception():

    with SimpleRuleRunner():
        r = Rule()
        m = MagicMock()
        m_exception = MagicMock(side_effect=ValueError)
        assert not m.called
        assert not m_exception.called
        r.register_on_unload(lambda : 1 / 0)

        def asdf():
            1 / 0

        r.register_on_unload(asdf)
        r.register_on_unload(m_exception)
        r.register_on_unload(m)
    assert m.called
    assert m.m_exception


if __name__ == '__main__':
    unittest.main()
