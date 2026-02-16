from __future__ import annotations

import logging

# noinspection PyProtectedMember
from sys import _getframe as sys_get_frame
from typing import TYPE_CHECKING, Any, Final


if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from collections.abc import Callable
    from types import FrameType, TracebackType

    from HABApp import Rule
    from HABApp.core.internals import EventBus, ExecutorFactory, ItemRegistry
    from HABApp.rule.interfaces.http_client import HABAppHttpClient
    from HABApp.rule_manager import RuleFile, RuleManager


_NAME: Final = '__HABAPP__HOOK__'


log = logging.getLogger('HABApp.Rule')


class HABAppRuleHook:

    def __init__(self,
                 cb_register_rule: Callable[[Rule], Any], cb_suggest_name: Callable[[Rule], str],
                 rule_manager: RuleManager, rule_file: RuleFile, loop: AbstractEventLoop,
                 async_http_client: HABAppHttpClient, item_registry: ItemRegistry, event_bus: EventBus,
                 executor_factory: ExecutorFactory) -> None:

        # callbacks
        self._cb_register: Final = cb_register_rule
        self._cb_suggest_name: Final = cb_suggest_name

        # runtime objs
        self.rule_manager: Final = rule_manager
        self.rule_file: Final = rule_file
        self.async_http_client: Final = async_http_client
        self.item_registry: Final = item_registry
        self.event_bus: Final = event_bus
        self.executor_factory: Final = executor_factory

        # asyncio
        self.event_loop: Final = loop

        # hook state
        self._is_closed: bool = False

    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        self._is_closed = True

    def register_rule(self, rule: Rule) -> None:
        if self._is_closed:
            # if we keep adding rules dynamically they will always get attached to the file and never unloaded
            log.warning(f'Added another rule of type {rule.__class__.__name__:s} '
                        'but file load has already been completed!')
        self._cb_register(rule)
        return None

    def suggest_rule_name(self, rule: Rule) -> str:
        return self._cb_suggest_name(rule)

    def in_dict(self, obj: dict | None = None) -> dict:
        if obj is None:
            obj = {}
        obj[_NAME] = self
        return obj


def get_rule_hook() -> HABAppRuleHook:

    # noinspection PyUnresolvedReferences
    frame: FrameType | None = sys_get_frame(1)

    while frame is not None:
        _globals = frame.f_globals

        if (hook := _globals.get(_NAME)) is not None:
            if not isinstance(hook, HABAppRuleHook):
                raise TypeError()
            return hook

        frame = frame.f_back

    msg = (
        'HABApp rule files are not meant to be executed directly! '
        'Put the file in the HABApp "rule" folder and HABApp will load it automatically.'
    )
    raise RuntimeError(msg)
