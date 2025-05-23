import logging
import re
import sys
import warnings
from collections.abc import Callable, Iterable
from pathlib import Path
from re import Pattern
from typing import Any, Final, Literal, ParamSpec, TypeVar, overload

import HABApp
import HABApp.core
import HABApp.openhab
import HABApp.rule_manager
import HABApp.util
from HABApp.core.asyncio import create_task
from HABApp.core.const.hints import TYPE_EVENT_CALLBACK
from HABApp.core.internals import (
    ContextBoundEventBusListener,
    ContextProvidingObj,
    EventBusListener,
    EventFilterBase,
    uses_item_registry,
    uses_post_event,
    wrap_func,
)
from HABApp.core.items import BaseItem, BaseValueItem
from HABApp.rule import interfaces
from HABApp.rule.scheduler.job_builder import HABAppJobBuilder as _HABAppJobBuilder

from .interfaces import async_subprocess_exec
from .interfaces.rule_subprocess import (
    HINT_EXEC_ARGS,
    HINT_PROCESS_CB_FULL,
    HINT_PROCESS_CB_SIMPLE,
    HINT_PYTHON_PATH,
    build_exec_params,
)
from .rule_hook import get_rule_hook as _get_rule_hook


log = logging.getLogger('HABApp.Rule')


# Func to log deprecation warnings
def send_warnings_to_log(message, category, filename, lineno, file=None, line=None) -> None:
    log.warning(f'{filename}:{lineno}: {category.__name__}:{message}')
    return



# Setup deprecation warnings
warnings.simplefilter('default')
warnings.showwarning = send_warnings_to_log


post_event = uses_post_event()
item_registry = uses_item_registry()


ITEM_TYPE = TypeVar('ITEM_TYPE', bound=BaseItem)


class Rule(ContextProvidingObj):

    def __init__(self) -> None:
        super().__init__(context=HABApp.rule_ctx.HABAppRuleContext(self))

        hook = _get_rule_hook()
        hook.register_rule(self)

        self.__runtime: HABApp.runtime.Runtime = hook.runtime
        assert isinstance(self.__runtime, HABApp.runtime.Runtime)

        # scheduler
        self.run: Final = _HABAppJobBuilder(self._habapp_ctx)

        # suggest a rule name
        self.rule_name: str = hook.suggest_rule_name(self)

        # interfaces
        self.async_http = interfaces.http
        self.mqtt: Final = HABApp.mqtt.interface_sync
        self.oh: Final = HABApp.openhab.interface_sync
        self.openhab: Final = self.oh

    def on_rule_loaded(self) -> None:
        """Override this to method to implement logic that will be called when
        the rule and the file has been successfully loaded. Can be sync or async.
        """

    def on_rule_removed(self) -> None:
        """Override this method to implement logic that will be called when the rule has been unloaded.
        Can be sync or async.
        """

    def __repr__(self) -> str:
        # empty string, so we have a space if we have more than one entry
        parts = ['']

        # rule name if it is different from the class
        cls_name = self.__class__.__name__
        rule_name = str(self.rule_name)
        if cls_name != rule_name:
            parts.append(rule_name)

        # rule status
        if self._habapp_ctx is None:
            parts.append('(unloaded)')

        return f'<{cls_name}{" ".join(parts)}>'

    def post_event(self, name: BaseItem | str, event: Any) -> None:
        """
        Post an event to the event bus

        :param name: name or item to post event to
        :param event: Event class to be used (must be class instance)
        :return:
        """
        assert isinstance(name, (str, BaseValueItem)), type(name)
        return post_event(
            name.name if isinstance(name, BaseValueItem) else name,
            event
        )

    def listen_event(self, name: BaseItem | str,
                     callback: TYPE_EVENT_CALLBACK,
                     event_filter: EventFilterBase | None = None
                     ) -> EventBusListener:
        """
        Register an event listener

        :param name: item or name to listen to
        :param callback: callback that accepts one parameter which will contain the event
        :param event_filter: Event filter. This is typically :class:`~HABApp.core.events.ValueUpdateEventFilter` or
            :class:`~HABApp.core.events.ValueChangeEventFilter` which will also trigger on changes/update from openhab
            or mqtt. Additionally it can be an instance of :class:`~HABApp.core.events.EventFilter` which additionally
            filters on the values of the event. It is also possible to group filters logically with, e.g.
            :class:`~HABApp.core.events.AndFilterGroup` and :class:`~HABApp.core.events.OrFilterGroup`
        """
        cb = wrap_func(callback, context=self._habapp_ctx)
        name = name.name if isinstance(name, BaseItem) else name

        if event_filter is None:
            event_filter = HABApp.core.events.NoEventFilter()
        if not isinstance(event_filter, EventFilterBase):
            msg = f'Argument event_filter must be an instance of event filter (is {event_filter})'
            raise TypeError(msg)

        listener = ContextBoundEventBusListener(name, cb, event_filter, parent_ctx=self._habapp_ctx)
        return self._habapp_ctx.add_event_listener(listener)

    @overload
    def execute_subprocess(self, callback: HINT_PROCESS_CB_SIMPLE, program: HINT_EXEC_ARGS, *args: HINT_EXEC_ARGS,
                           additional_python_path: HINT_PYTHON_PATH = None, capture_output: bool = True,
                           raw_info: Literal[False], **kwargs) -> None:
        ...

    @overload
    def execute_subprocess(self, callback: HINT_PROCESS_CB_FULL, program: HINT_EXEC_ARGS, *args: HINT_EXEC_ARGS,
                           additional_python_path: HINT_PYTHON_PATH = None, capture_output: bool = True,
                           raw_info: Literal[True], **kwargs) -> None:
        ...

    def execute_subprocess(self, callback, program: HINT_EXEC_ARGS, *args: HINT_EXEC_ARGS,
                           additional_python_path: HINT_PYTHON_PATH = None, capture_output: bool = True,
                           raw_info: bool = False, **kwargs):
        """Run another program

        :param callback: Function that will be called when the process has finished.
                         First parameter takes a :class:`str` when :attr:`raw_info` is ``False`` (default) else
                         an instance of :class:`~HABApp.rule.FinishedProcessInfo`
        :param program: python module (path to file) or python package
        :param args: arguments passed to the module or to package
        :param raw_info: ``False``: Return only the textual process output.
                         In case of failure (return code != 0) a log entry and an error event will be created.
                         This is the default and should be fine for almost all use cases.

                         ``True``: The callback will always be called with an
                         instance of :class:`~HABApp.rule.FinishedProcessInfo`.
        :param capture_output: Capture program output, set to ``False`` to only capture the return code
        :param additional_python_path: additional folders which will be added to the env variable ``PYTHONPATH``
        :param kwargs: Additional kwargs that will be passed to ``asyncio.create_subprocess_exec``
        :return:
        """

        cb = wrap_func(callback, context=self._habapp_ctx)

        call_args, call_kwargs = build_exec_params(
            program, *args, _capture_output=capture_output, _additional_python_path=additional_python_path, **kwargs
        )
        return create_task(
            async_subprocess_exec(
                cb.run, *call_args, raw_info=raw_info, calling_func=self.execute_python, **call_kwargs)
        )

    @overload
    def execute_python(self, callback: HINT_PROCESS_CB_SIMPLE, module_or_package: HINT_EXEC_ARGS, *args: HINT_EXEC_ARGS,
                       additional_python_path: HINT_PYTHON_PATH = None, capture_output: bool = True,
                       raw_info: Literal[False], **kwargs) -> None:
        ...

    @overload
    def execute_python(self, callback: HINT_PROCESS_CB_FULL, module_or_package: HINT_EXEC_ARGS, *args: HINT_EXEC_ARGS,
                       additional_python_path: HINT_PYTHON_PATH = None, capture_output: bool = True,
                       raw_info: Literal[True], **kwargs) -> None:
        ...

    def execute_python(self, callback, module_or_package: HINT_EXEC_ARGS, *args: HINT_EXEC_ARGS,
                       additional_python_path: HINT_PYTHON_PATH = None, capture_output: bool = True,
                       raw_info: bool = False, **kwargs):
        """Run a python module or package as a new process. The python environment that is used to run HABApp will be
        to run the module or package.

        :param callback: Function that will be called when the process has finished.
                         First parameter takes a :class:`str` when :attr:`raw_info` is ``False`` (default) else
                         an instance of :class:`~HABApp.rule.FinishedProcessInfo`
        :param module_or_package: python module (path to file) or python package (just the name)
        :param args: arguments passed to the module or to package
        :param raw_info: ``False``: Return only the textual process output.
                         In case of failure (return code != 0) a log entry and an error event will be created.
                         This is the default and should be fine for almost all use cases.

                         ``True``: The callback will always be called with an
                         instance of :class:`~HABApp.rule.FinishedProcessInfo`.
        :param capture_output: Capture program output, set to ``False`` to only capture the return code
        :param additional_python_path: additional folders which will be added to the env variable ``PYTHONPATH``
        :param kwargs: Additional kwargs that will be passed to ``asyncio.create_subprocess_exec``
        :return:
        """

        new_args = list(args)

        p = Path(module_or_package)
        if p.suffix.lower() == '.py':
            # if it's a relative path make it relative to the config
            if not p.is_absolute():
                p = (HABApp.CONFIG._file_path.parent / p).resolve()

            new_args.insert(0, p)

            # set parent folder as working directory for python script
            if 'cwd' not in kwargs:
                kwargs['cwd'] = p.parent
        else:
            new_args.insert(0, module_or_package)
            new_args.insert(0, '-m')

        cb = wrap_func(callback, context=self._habapp_ctx)
        call_args, call_kwargs = build_exec_params(
            sys.executable, *new_args,
            _capture_output=capture_output, _additional_python_path=additional_python_path,
            **kwargs
        )

        return create_task(
            async_subprocess_exec(
                cb.run, *call_args, raw_info=raw_info, calling_func=self.execute_python, **call_kwargs)
        )

    def get_rule(self, rule_name: str) -> 'Rule | list[Rule]':
        assert rule_name is None or isinstance(rule_name, str), type(rule_name)
        return self.__runtime.rule_manager.get_rule(rule_name)

    @staticmethod
    def get_items(type: tuple[type[ITEM_TYPE], ...] | type[ITEM_TYPE] | None = None,
                  name: str | Pattern[str] | None = None,
                  tags: str | Iterable[str] | None = None,
                  groups: str | Iterable[str] | None = None,
                  metadata: str | Pattern[str] | None = None,
                  metadata_value: str | Pattern[str] | None = None,
                  ) -> list[ITEM_TYPE] | list[BaseItem]:
        """Search the HABApp item registry and return the found items.

        :param type: item has to be an instance of this class
        :param name: str (will be compiled) or regex that is used to search the Name
        :param tags: item must have these tags (will return only instances of OpenhabItem)
        :param groups: item must be a member of these groups (will return only instances of OpenhabItem)
        :param metadata: str (will be compiled) or regex that is used to search the metadata (e.g. 'homekit')
        :param metadata_value: str (will be compiled) or regex that is used to search the metadata value
                               (e.g. 'TargetTemperature')
        :return: Items that match all the passed criteria
        """

        if name is not None and isinstance(name, str):
            name = re.compile(name, re.IGNORECASE)
        if metadata is not None and isinstance(metadata, str):
            metadata = re.compile(metadata, re.IGNORECASE)
        if metadata_value is not None and isinstance(metadata_value, str):
            metadata_value = re.compile(metadata_value, re.IGNORECASE)

        _tags, _groups = None, None
        if tags is not None:
            _tags = set(tags) if not isinstance(tags, str) else {tags}
        if groups is not None:
            _groups = set(groups) if not isinstance(groups, str) else {groups}

        OpenhabItem = HABApp.openhab.items.OpenhabItem
        if _tags or _groups or metadata or metadata_value:
            if type is None:
                type = OpenhabItem
            if not issubclass(type, OpenhabItem):
                msg = 'Searching for tags, groups and metadata only works for OpenhabItem or its subclasses'
                raise ValueError(msg)

        ret = []
        for item in item_registry.get_items():  # type: HABApp.core.items.BaseItem
            if type is not None and not isinstance(item, type):
                continue

            if name is not None and not name.search(item.name):
                continue

            if _tags is not None and not _tags.issubset(item.tags):
                continue

            if _groups is not None and not _groups.issubset(item.groups):
                continue

            if metadata is not None and not any(map(metadata.search, item.metadata)):
                continue

            if metadata_value is not None and not any(
                    map(metadata_value.search, map(lambda x: x[0], item.metadata.values()))):
                continue

            ret.append(item)
        return ret


PSPEC_RULE = ParamSpec('PSPEC_RULE')
TYPE_RULE = TypeVar('TYPE_RULE', bound=Rule)


def create_rule(f: Callable[PSPEC_RULE, TYPE_RULE], *args: PSPEC_RULE.args, **kwargs: PSPEC_RULE.kwargs) -> TYPE_RULE:
    try:
        _get_rule_hook()
    except RuntimeError:
        return None

    return f(*args, **kwargs)
