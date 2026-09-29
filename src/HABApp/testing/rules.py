from typing import Final, overload

from HABApp import Rule


class RuleRegistry:
    def __init__(self) -> None:
        self.rules: Final[list[Rule]] = []

    def register_rule(self, obj: Rule) -> None:
        self.rules.append(obj)

    @staticmethod
    def suggest_rule_name(obj: object) -> str:
        return f'Testing.{obj.__class__.__name__}'

    @overload
    def get_rule(self, name: str) -> Rule: ...

    @overload
    def get_rule(self, name: None) -> list[Rule]: ...

    def get_rule(self, name: str | None) -> Rule | list[Rule]:
        if name is None:
            return self.rules.copy()

        found = [r for r in self.rules if r.rule_name == name]
        if not found:
            msg = f'No Rule with name "{name}" found!'
            raise KeyError(msg)
        if len(found) > 1:
            msg = f'Multiple Rules with name "{name}" found!'
            raise KeyError(msg)

        return found[0]
