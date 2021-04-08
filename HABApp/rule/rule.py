import asyncio
import datetime
import logging
import random
import sys
import traceback
import typing
import warnings
import weakref

import HABApp
import HABApp.core
import HABApp.openhab
import HABApp.rule_manager
import HABApp.util
from HABApp.core.events import AllEvents
from .interfaces import async_subprocess_exec
from HABApp.rule.habappscheduler import HABAppScheduler


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

        self.__event_listener: typing.List[HABApp.core.EventBusListener] = []
        self.__unload_functions: typing.List[typing.Callable[[], None]] = []
        self.__cancel_objs: weakref.WeakSet = weakref.WeakSet()

        # schedule cleanup of this rule
        self.register_on_unload(self.__cleanup_rule)
        self.register_on_unload(self.__cleanup_objs)

        # scheduler
        self.run: HABAppScheduler = HABAppScheduler(self)

        # suggest a rule name if it is not
        self.rule_name: str = self.__rule_file.suggest_rule_name(self)

        # interfaces
        self.async_http: HABApp.rule.interfaces.AsyncHttpConnection = self.__runtime.async_http if not test else None
        self.mqtt: HABApp.mqtt.interface = HABApp.mqtt.interface
        self.oh: HABApp.openhab.interface = HABApp.openhab.interface
        self.openhab: HABApp.openhab.interface = self.oh

    @HABApp.core.wrapper.log_exception
    def __cleanup_objs(self):
        while self.__cancel_objs:
            # we log each error as warning
            with HABApp.core.wrapper.ExceptionToHABApp(log, logging.WARNING):
                obj = self.__cancel_objs.pop()
                obj.cancel()

    @HABApp.core.wrapper.log_exception
    def __cleanup_rule(self):
        # Important: set the dicts to None so we don't schedule a future event during _cleanup.
        # If dict is set to None we will crash instead but it is no problem because everything gets unloaded anyhow
        event_listeners = self.__event_listener
        self.__event_listener = None

        # Actually remove the listeners/events
        for listener in event_listeners:
            HABApp.core.EventBus.remove_listener(listener)

        return None

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

    def listen_event(self, name: typing.Union[HABApp.core.items.BaseValueItem, str],
                     callback: typing.Callable[[typing.Any], typing.Any],
                     event_type: typing.Union[typing.Type['HABApp.core.events.AllEvents'],
                                              'HABApp.core.events.EventFilter', typing.Any] = AllEvents
                     ) -> HABApp.core.EventBusListener:
        """
        Register an event listener

        :param name: item or name to listen to. Use None to listen to all events
        :param callback: callback that accepts one parameter which will contain the event
        :param event_type: Event filter. This is typically :class:`~HABApp.core.events.ValueUpdateEvent` or
            :class:`~HABApp.core.events.ValueChangeEvent` which will also trigger on changes/update from openhab
            or mqtt. Additionally it can be an instance of :class:`~HABApp.core.events.EventFilter` which additionally
            filters on the values of the event. There are also templates for the most common filters, e.g.
            :class:`~HABApp.core.events.ValueUpdateEventFilter` and :class:`~HABApp.core.events.ValueChangeEventFilter`
        """
        cb = HABApp.core.WrappedFunction(callback, name=self._get_cb_name(callback))
        name = name.name if isinstance(name, HABApp.core.items.BaseValueItem) else name

        if isinstance(event_type, HABApp.core.events.EventFilter):
            listener = event_type.create_event_listener(name, cb)
        else:
            listener = HABApp.core.EventBusListener(name, cb, event_type)

        self.__event_listener.append(listener)
        HABApp.core.EventBus.add_listener(listener)
        return listener

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
        cb = HABApp.core.WrappedFunction(callback, name=self._get_cb_name(callback))

        asyncio.run_coroutine_threadsafe(
            async_subprocess_exec(cb.run, program, *args, capture_output=capture_output),
            HABApp.core.const.loop
        )

    def get_rule(self, rule_name: str) -> 'typing.Union[Rule, typing.List[Rule]]':
        assert rule_name is None or isinstance(rule_name, str), type(rule_name)
        return self.__runtime.rule_manager.get_rule(rule_name)

    def register_on_unload(self, func: typing.Callable[[], typing.Any]):
        """Register a function with no parameters which will be called when the rule is unloaded.
        Use this for custom cleanup functions.

        :param func: function which will be called
        """
        assert callable(func)
        assert func not in self.__unload_functions, 'Function was already registered!'
        self.__unload_functions.append(func)

    def register_cancel_obj(self, obj):
        """Add a ``weakref`` to an obj which has a ``cancel`` function.
        When the rule gets unloaded the cancel function will be called (if the obj was not already garbage collected)

        :param obj:
        """
        self.__cancel_objs.add(obj)

    # -----------------------------------------------------------------------------------------------------------------
    # deprecated functions
    # -----------------------------------------------------------------------------------------------------------------
    def run_every(self, time, interval: typing.Union[int, datetime.timedelta],
                  callback, *args, **kwargs):
        warnings.warn('self.run_every is deprecated. Please use self.run.every', DeprecationWarning)
        return self.run.every(time, interval, callback, *args, **kwargs)

    def run_on_sun(self, sun_event: str, callback, *args, **kwargs):
        warnings.warn('self.run_on_sun is deprecated. Please use self.run.on_sunrise, self.run.on_sunset, ...',
                      DeprecationWarning)
        func = {'sunset': self.run.on_sunset, 'sunrise': self.run.on_sunrise,
                'dusk': self.run.on_sun_dusk, 'dawn': self.run.on_sun_dawn}
        return func[sun_event](callback, *args, **kwargs)

    def run_on_day_of_week(self, time: datetime.time, weekdays, callback, *args, **kwargs):
        warnings.warn('self.run_on_day_of_week is deprecated. Please use self.run.on_day_of_week', DeprecationWarning)
        return self.run.on_every_day(time, weekdays, callback, *args, **kwargs)

    def run_on_every_day(self, time: datetime.time, callback, *args, **kwargs):
        warnings.warn('self.run_on_every_day is deprecated. Please use self.run.on_every_day', DeprecationWarning)
        return self.run.on_every_day(time, callback, *args, **kwargs)

    def run_on_workdays(self, time: datetime.time, callback, *args, **kwargs):
        warnings.warn('self.run_on_workdays is deprecated. Please use self.run.on_workdays', DeprecationWarning)
        return self.run.on_workdays(time, callback, *args, **kwargs)

    def run_on_weekends(self, time: datetime.time, callback, *args, **kwargs):
        warnings.warn('self.run_on_weekends is deprecated. Please use self.run.on_weekends', DeprecationWarning)
        return self.run.on_weekends(time, callback, *args, **kwargs)

    def run_daily(self, callback, *args, **kwargs):
        warnings.warn('self.run_hourly is deprecated. Please use self.run.every', DeprecationWarning)
        start = datetime.timedelta(seconds=random.randint(0, 24 * 3600 - 1))
        return self.run.every(start, datetime.timedelta(days=1), callback, *args, **kwargs)

    def run_hourly(self, callback, *args, **kwargs) :
        warnings.warn('self.run_hourly is deprecated. Please use self.run.every_hour', DeprecationWarning)
        return self.run.every_hour(callback, *args, **kwargs)

    def run_minutely(self, callback, *args, **kwargs):
        warnings.warn('self.run_minutely is deprecated. Please use self.run.every_minute', DeprecationWarning)
        return self.run.every_minute(callback, *args, **kwargs)

    def run_at(self, date_time, callback, *args, **kwargs):
        warnings.warn('self.run_at is deprecated. Please use self.run.at', DeprecationWarning)
        return self.run.at(date_time, callback, *args, **kwargs)

    def run_in(self, seconds: typing.Union[int, datetime.timedelta], callback, *args, **kwargs):
        warnings.warn('self.run_in is deprecated. Please use self.run.at', DeprecationWarning)
        return self.run.at(seconds, callback, *args, **kwargs)

    def run_soon(self, callback, *args, **kwargs):
        warnings.warn('self.run_in is deprecated. Please use self.run.at', DeprecationWarning)
        return self.run.soon(callback, *args, **kwargs)

    # -----------------------------------------------------------------------------------------------------------------
    # internal functions
    # -----------------------------------------------------------------------------------------------------------------
    def _get_cb_name(self, callback):
        return f'{self.rule_name}.{callback.__name__}' if self.rule_name else None

    def _add_event_listener(self, listener: HABApp.core.EventBusListener) -> HABApp.core.EventBusListener:
        self.__event_listener.append(listener)
        HABApp.core.EventBus.add_listener(listener)
        return listener

    @HABApp.core.wrapper.log_exception
    def _check_rule(self):

        # Check if items do exists
        if not HABApp.core.Items.get_all_items():
            return None

        for listener in self.__event_listener:

            # Internal topics - don't warn there
            if listener.topic in HABApp.core.const.topics.ALL:
                continue

            # check if specific item exists
            if not HABApp.core.Items.item_exists(listener.topic):
                log.warning(f'Item "{listener.topic}" does not exist (yet)! '
                            f'self.listen_event in "{self.rule_name}" may not work as intended.')

    @HABApp.core.wrapper.log_exception
    def _unload(self):

        # unload all functions
        for func in self.__unload_functions:
            try:
                func()
            except Exception as e:

                # try getting function name
                try:
                    name = f' in "{func.__name__}"'
                except AttributeError:
                    name = ''

                log.error(f'Error{name} while unloading "{self.rule_name}": {e}')

                # log traceback
                lines = traceback.format_exc().splitlines()
                del lines[1:3]  # see implementation in wrappedfunction.py why we do this
                for line in lines:
                    log.error(line)


@HABApp.core.wrapper.log_exception
def get_parent_rule() -> Rule:
    depth = 1
    while True:
        try:
            frm = sys._getframe(depth)
        except ValueError:
            raise RuntimeError('Could not find parent rule!') from None

        __vars = frm.f_locals
        depth += 1
        if 'self' in __vars:
            rule = __vars['self']
            if isinstance(rule, Rule):
                return rule
