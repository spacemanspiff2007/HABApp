# ruff: noqa: S101
import HABApp
from HABApp.testing.conftest import *  # noqa: F403


class RuleWithParameter(HABApp.Rule):
    def __init__(self) -> None:
        super().__init__()
        self.value = HABApp.Parameter('tests_user_param_file', 'key', default_value=123)


def test_parameter_in_rule(testing_rules) -> None:
    rule = RuleWithParameter()
    assert rule.value == 123
