import asyncio
import logging
import re
import sys
import typing
import warnings
from typing import Iterable, Union

import HABApp
import HABApp.core
import HABApp.openhab
import HABApp.rule_manager
import HABApp.util
from HABApp.core.events import AllEvents
from HABApp.core.items.base_item import BaseItem, TYPE_ITEM, TYPE_ITEM_CLS
from HABApp.rule import interfaces
from HABApp.rule.scheduler import HABAppSchedulerView as _HABAppSchedulerView
from .interfaces import async_subprocess_exec

log = logging.getLogger('HABApp.Rule')


# Func to log deprecation warnings
def send_warnings_to_log(message, category, filename, lineno, file=None, line=None):
    log.warning('%s:%s: %s:%s' % (filename, lineno, category.__name__, message))
    return


# Setup deprecation warnings
warnings.simplefilter('default')
warnings.showwarning = send_warnings_to_log


class Rule:
    def __init__(self):

        # get the variables from the caller
        depth = 1
        while True:
            try:
                __vars = sys._getframe(depth).f_globals
            except ValueError:
                raise RuntimeError('Rule files are not meant to be executed directly! '
                                   'Put the file in the HABApp "rule" folder and HABApp will load it automatically.')

            depth += 1
            if '__HABAPP__RUNTIME__' in __vars:
                __runtime__ = __vars['__HABAPP__RUNTIME__']
                __rule_file__ = __vars['__HABAPP__RULE_FILE__']
                break

        # variable vor unittests
        test = __vars.get('__UNITTEST__', False)

        # this is a list which contains all rules of this file
        __vars['__HABAPP__RULES'].append(self)

        assert isinstance(__runtime__, HABApp.runtime.Runtime)
        self.__runtime: HABApp.runtime.Runtime = __runtime__

        if not test:
            assert isinstance(__rule_file__, HABApp.rule_manager.RuleFile)
        self.__rule_file: HABApp.rule_manager.RuleFile = __rule_file__

        # context
        self._habapp_rule_ctx = HABApp.rule_ctx.HABAppRuleContext(self)

        # scheduler
        self.run: _HABAppSchedulerView = _HABAppSchedulerView(self._habapp_rule_ctx)

        # suggest a rule name
        self.rule_name: str = self.__rule_file.suggest_rule_name(self)

        # interfaces
        self.async_http = interfaces.http
        self.mqtt: HABApp.mqtt.interface = HABApp.mqtt.interface
        self.oh: HABApp.openhab.interface = HABApp.openhab.interface
        self.openhab: HABApp.openhab.interface = self.oh

    def on_rule_load(self):
        """Override this to implement logic that will be called when the rule and the file has been successfully loaded
        """

    def on_rule_unload(self):
        """Override this to implement logic that will be called when the rule has been unloaded.
        """

    def post_event(self, name, event):
        """
        Post an event to the event bus

        :param name: name or item to post event to
        :param event: Event class to be used (must be class instance)
        :return:
        """
        assert isinstance(name, (str, HABApp.core.items.BaseValueItem)), type(name)
        return HABApp.core.EventBus.post_event(
            name.name if isinstance(name, HABApp.core.items.BaseValueItem) else name,
            event
        )

    def listen_event(self, name: Union[HABApp.core.items.BaseValueItem, str],
                     callback: typing.Callable[[typing.Any], typing.Any],
                     event_type: Union[typing.Type['HABApp.core.events.AllEvents'],
                                       'HABApp.core.events.EventFilter', typing.Any] = AllEvents
                     ) -> HABApp.core.EventBusListener:
        """
        Register an event listener

        :param name: item or name to listen to
        :param callback: callback that accepts one parameter which will contain the event
        :param event_type: Event filter. This is typically :class:`~HABApp.core.events.ValueUpdateEvent` or
            :class:`~HABApp.core.events.ValueChangeEvent` which will also trigger on changes/update from openhab
            or mqtt. Additionally it can be an instance of :class:`~HABApp.core.events.EventFilter` which additionally
            filters on the values of the event. There are also templates for the most common filters, e.g.
            :class:`~HABApp.core.events.ValueUpdateEventFilter` and :class:`~HABApp.core.events.ValueChangeEventFilter`
        """
        cb = HABApp.core.WrappedFunction(callback, rule_ctx=self._habapp_rule_ctx)
        name = name.name if isinstance(name, HABApp.core.items.BaseValueItem) else name

        if isinstance(event_type, HABApp.core.events.EventFilter):
            listener = event_type.create_event_listener(name, cb)
        else:
            listener = HABApp.core.EventBusListener(name, cb, event_type)

        return self._habapp_rule_ctx.add_event_listener(listener)

    def execute_subprocess(self, callback, program, *args, capture_output=True):
        """Run another program

        :param callback: |param_scheduled_cb| after process has finished. First parameter will
                         be an instance of :class:`~HABApp.rule.FinishedProcessInfo`
        :param program: program or path to program to run
        :param args: |param_scheduled_cb_args|
        :param capture_output: Capture program output, set to `False` to only capture return code
        :return:
        """

        assert isinstance(program, str), type(program)
        cb = HABApp.core.WrappedFunction(callback, rule_ctx=self._habapp_rule_ctx)

        asyncio.run_coroutine_threadsafe(
            async_subprocess_exec(cb.run, program, *args, capture_output=capture_output),
            HABApp.core.const.loop
        )

    def get_rule(self, rule_name: str) -> 'Union[Rule, typing.List[Rule]]':
        assert rule_name is None or isinstance(rule_name, str), type(rule_name)
        return self.__runtime.rule_manager.get_rule(rule_name)

    @staticmethod
    def get_items(type: Union[typing.Tuple[TYPE_ITEM_CLS, ...], TYPE_ITEM_CLS] = None,
                  name: Union[str, typing.Pattern[str]] = None,
                  tags: Union[str, Iterable[str]] = None,
                  groups: Union[str, Iterable[str]] = None,
                  metadata: Union[str, typing.Pattern[str]] = None,
                  metadata_value: Union[str, typing.Pattern[str]] = None,
                  ) -> Union[typing.List[TYPE_ITEM], typing.List[BaseItem]]:
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
                raise ValueError('Searching for tags, groups and metadata only works for OpenhabItem or its Subclasses')

        ret = []
        for item in HABApp.core.Items.get_items():  # type: HABApp.core.items.base_valueitem.BaseItem
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
