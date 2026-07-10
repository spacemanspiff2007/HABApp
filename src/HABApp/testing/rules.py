from typing import Final

from HABApp import Rule


class RuleRegistry:
    def __init__(self) -> None:
        self.rules: Final[list[Rule]] = []

    def register_rule(self, obj: Rule) -> None:
        self.rules.append(obj)

    @staticmethod
    def suggest_rule_name(obj: object) -> str:
        return f'Testing.{obj.__class__.__name__}'
