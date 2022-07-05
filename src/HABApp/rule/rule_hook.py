import sys
from typing import TYPE_CHECKING, Any, Callable, Final


if TYPE_CHECKING:
    import HABApp
    import types
    import HABApp.rule_manager

_NAME: Final = '__HABAPP__HOOK__'


class HABAppRuleHook:

    @classmethod
    def in_dict(cls, obj: dict,
                cb_register_rule: Callable[['HABApp.rule.Rule'], Any],
                cb_suggest_name: Callable[['HABApp.rule.Rule'], str],
                runtime: 'HABApp.runtime.Runtime', rule_file: 'HABApp.rule_manager.RuleFile') -> dict:
        obj[_NAME] = cls(cb_register_rule, cb_suggest_name, runtime, rule_file)
        return obj

    def __init__(self,
                 cb_register_rule: Callable[['HABApp.rule.Rule'], Any],
                 cb_suggest_name: Callable[['HABApp.rule.Rule'], str],
                 runtime: 'HABApp.runtime.Runtime', rule_file: 'HABApp.rule_manager.RuleFile'):
        # callbacks
        self._cb_register: Final = cb_register_rule
        self._cb_suggest_name: Final = cb_suggest_name

        # runtime objs
        self.runtime: Final = runtime
        self.rule_file: Final = rule_file

    def register_rule(self, rule: 'HABApp.rule.Rule'):
        return self._cb_register(rule)

    def suggest_rule_name(self, rule: 'HABApp.rule.Rule') -> str:
        return self._cb_suggest_name(rule)


def get_rule_hook() -> HABAppRuleHook:

    depth = 0
    while True:
        depth += 1
        try:
            frame = sys._getframe(depth)    # type: types.FrameType
        except ValueError:
            raise RuntimeError('Rule files are not meant to be executed directly! '
                               'Put the file in the HABApp "rule" folder and HABApp will load it automatically.')

        _globals = frame.f_globals

        hook = _globals.get(_NAME, None)
        if hook is None:
            continue

        assert isinstance(hook, HABAppRuleHook)
        return hook
