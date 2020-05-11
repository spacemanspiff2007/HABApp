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
from .scheduler import ReoccurringScheduledCallback, OneTimeCallback, DayOfWeekScheduledCallback, \
    TYPING_DATE_TIME, SunScheduledCallback
from .scheduler.base import ScheduledCallbackBase as _ScheduledCallbackBase


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
            __vars = sys._getframe(depth).f_globals
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
        self.__future_events: typing.List[_ScheduledCallbackBase] = []
        self.__unload_functions: typing.List[typing.Callable[[], None]] = []
        self.__cancel_objs: weakref.WeakSet = weakref.WeakSet()

        # schedule cleanup of this rule
        self.register_on_unload(self.__cleanup_rule)
        self.register_on_unload(self.__cleanup_objs)


        # suggest a rule name if it is not
        self.rule_name: str = self.__rule_file.suggest_rule_name(self)

        # interfaces
        self.async_http: HABApp.rule.interfaces.AsyncHttpConnection = self.__runtime.async_http if not test else None
        self.mqtt = self.__runtime.mqtt_connection.interface if not test else None
        self.oh: HABApp.openhab.OpenhabInterface = HABApp.openhab.get_openhab_interface() if not test else None
        self.openhab: HABApp.openhab.OpenhabInterface = self.oh

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
        future_events = self.__future_events

        self.__event_listener = None
        self.__future_events = None

        # Actually remove the listeners/events
        for listener in event_listeners:
            HABApp.core.EventBus.remove_listener(listener)

        for event in future_events:
            event.cancel()
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
                     event_type: typing.Union[AllEvents, typing.Any] = AllEvents
                     ) -> HABApp.core.EventBusListener:
        """
        Register an event listener

        :param name: item or name to listen to. Use None to listen to all events
        :param callback: callback that accepts one parameter which will contain the event
        :param event_type: Event filter. This is typically :class:`~HABApp.core.ValueUpdateEvent` or
            :class:`~HABApp.core.ValueChangeEvent` which will also trigger on changes/update from openhab
            or mqtt.
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        listener = HABApp.core.EventBusListener(
            name.name if isinstance(name, HABApp.core.items.BaseValueItem) else name, cb, event_type
        )
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
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))

        asyncio.run_coroutine_threadsafe(
            async_subprocess_exec(cb.run, program, *args, capture_output=capture_output),
            HABApp.core.const.loop
        )

    def run_every(self,
                  time: TYPING_DATE_TIME, interval: typing.Union[int, datetime.timedelta],
                  callback, *args, **kwargs) -> ReoccurringScheduledCallback:
        """
        Run a function periodically

        :param time: |param_scheduled_time|
        :param interval:
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = ReoccurringScheduledCallback(cb, *args, **kwargs)
        future_event.interval(interval)
        self.__future_events.append(future_event)
        return future_event

    def run_on_sun(self, sun_event: str, callback, *args, run_if_missed=False, **kwargs) -> SunScheduledCallback:
        """Run a function on sunrise/sunset etc

        :param sun_event: 'sunrise', 'sunset', 'dusk', 'dawn'
        :param run_if_missed: run the event if we missed it for today
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = SunScheduledCallback(cb, *args, **kwargs)
        future_event.sun_trigger(sun_event)
        future_event._calculate_next_call()
        self.__future_events.append(future_event)
        return future_event

    def run_on_day_of_week(self,
                           time: datetime.time, weekdays, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: datetime.time
        :param weekdays:
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        assert isinstance(time, datetime.time), type(time)

        # names of weekdays in local language
        lookup = {datetime.date(2001, 1, i).strftime('%A'): i for i in range(1, 8)}
        lookup.update({datetime.date(2001, 1, i).strftime('%A')[:3]: i for i in range(1, 8)})

        # abbreviations in German and English
        lookup.update({"Mo": 1, "Di": 2, "Mi": 3, "Do": 4, "Fr": 5, "Sa": 6, "So": 7})
        lookup.update({"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7})
        lookup = {k.lower(): v for k, v in lookup.items()}

        if isinstance(weekdays, int) or isinstance(weekdays, str):
            weekdays = [weekdays]
        for i, val in enumerate(weekdays):
            if not isinstance(val, str):
                continue
            weekdays[i] = lookup[val.lower()]

        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays(weekdays)
        future_event.time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_on_every_day(self, time: datetime.time, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: datetime.time
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        assert isinstance(time, datetime.time), type(time)
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays([1, 2, 3, 4, 5, 6, 7])
        future_event.time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_on_workdays(self, time: datetime.time, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: datetime.time
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        assert isinstance(time, datetime.time), type(time)
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays('workday')
        future_event.time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_on_weekends(self, time: datetime.time, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: datetime.time
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        assert isinstance(time, datetime.time), type(time)
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays('weekend')
        future_event.time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_daily(self, callback, *args, **kwargs) -> ReoccurringScheduledCallback:
        """
        Picks a random hour, minute and second and runs the callback every day

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = datetime.timedelta(seconds=random.randint(0, 24 * 3600 - 1))
        interval = datetime.timedelta(days=1)
        return self.run_every(start, interval, callback, *args, **kwargs)

    def run_hourly(self, callback, *args, **kwargs) -> ReoccurringScheduledCallback:
        """
        Picks a random minute and second and run the callback every hour

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = datetime.timedelta(seconds=random.randint(0, 3600 - 1))
        interval = datetime.timedelta(seconds=3600)
        return self.run_every(start, interval, callback, *args, **kwargs)

    def run_minutely(self, callback, *args, **kwargs) -> ReoccurringScheduledCallback:
        """
        Picks a random second and runs the callback every minute

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        start = datetime.timedelta(seconds=random.randint(0, 60 - 1))
        interval = datetime.timedelta(seconds=60)
        return self.run_every(start, interval, callback, *args, **kwargs)

    def run_at(self, date_time: TYPING_DATE_TIME, callback, *args, **kwargs) -> OneTimeCallback:
        """
        Run a function at a specified date_time

        :param date_time:
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = OneTimeCallback(cb, *args, **kwargs)
        future_event.set_run_time(date_time)
        self.__future_events.append(future_event)
        return future_event

    def run_in(self, seconds: typing.Union[int, datetime.timedelta], callback, *args, **kwargs) -> OneTimeCallback:
        """
        Run the callback in x seconds

        :param int seconds: Wait time in seconds or a timedelta obj before calling the function
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        assert isinstance(seconds, (int, datetime.timedelta)), f'{seconds} ({type(seconds)})'
        fut = datetime.timedelta(seconds=seconds) if not isinstance(seconds, datetime.timedelta) else seconds

        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = OneTimeCallback(cb, *args, **kwargs)
        future_event.set_run_time(fut)
        self.__future_events.append(future_event)
        return future_event

    def run_soon(self, callback, *args, **kwargs) -> OneTimeCallback:
        """
        Run the callback as soon as possible (typically in the next second).

        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = OneTimeCallback(cb, *args, **kwargs)
        future_event.set_run_time(None)
        self.__future_events.append(future_event)
        return future_event

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
    def item_watch(self, name: typing.Union[str, HABApp.core.items.BaseValueItem],
                   seconds_constant: int, watch_only_changes=True):
        warnings.warn("'item_watch' is deprecated, use the 'watch_change' or 'watch_update'"
                      " method of the item instance instead", DeprecationWarning, 2)

        assert isinstance(seconds_constant, int)
        assert isinstance(watch_only_changes, bool)
        if isinstance(name, str):
            item = HABApp.core.items.BaseValueItem.get_item(name)
        else:
            assert isinstance(name, HABApp.core.items.BaseValueItem), type(name)
            item = name

        if watch_only_changes:
            return item.watch_change(seconds_constant)
        else:
            return item.watch_update(seconds_constant)


    def item_watch_and_listen(self, name: typing.Union[HABApp.core.items.BaseValueItem, str],
                              seconds_constant: int, callback, watch_only_changes=True
                              ):
        warnings.warn("'item_watch_and_listen' is deprecated, use the 'watch_change' or 'watch_update'"
                      " method of the item instance instead", DeprecationWarning, 2)

        watched_item = self.item_watch(name, seconds_constant, watch_only_changes)
        event_listener = self.listen_event(
            name,
            callback,
            HABApp.core.events.ItemNoChangeEvent if watch_only_changes else HABApp.core.events.ItemNoUpdateEvent
        )
        return watched_item, event_listener


    def item_exists(self, name: str) -> bool:
        warnings.warn("'item_exists' is deprecated!", DeprecationWarning, 2)
        assert isinstance(name, str), type(name)
        return HABApp.core.Items.item_exists(name)

    def get_item_state(self, name: str, default=None) -> typing.Any:
        warnings.warn("'get_item_state' is deprecated, use 'get_value' or 'value'"
                      " method of the item instance instead", DeprecationWarning, 2)

        if default is None:
            return HABApp.core.Items.get_item(name).value

        try:
            state = HABApp.core.Items.get_item(name).value
        except HABApp.core.Items.ItemNotFoundException:
            return default

        if state is None:
            return default
        return state

    def set_item_state(self, name: str, value: typing.Any):
        warnings.warn("'set_item_state' is deprecated, use 'post_value' or 'set_value' method "
                      "of the item instance instead", DeprecationWarning, 2)

        if isinstance(name, str):
            try:
                item = HABApp.core.Items.get_item(name)
            except HABApp.core.Items.ItemNotFoundException:
                item = HABApp.core.Items.create_item(name, HABApp.core.items.Item)
        else:
            assert isinstance(name, HABApp.core.items.Item)
            item = name

        item.post_value(value)
        return None

    def get_item(self, name: str, item_factory=None) -> HABApp.core.items.Item:

        warnings.warn("'get_item' is deprecated, use 'Item.get_item' or 'Item.get_create_item' instead",
                      DeprecationWarning, 2)

        if item_factory is None:
            return HABApp.core.Items.get_item(name)

        try:
            return HABApp.core.Items.get_item(name)
        except HABApp.core.Items.ItemNotFoundException:
            return HABApp.core.Items.create_item(name, item_factory)

    def get_rule_parameter(self, file_name: str, *keys, default_value='ToDo'):
        warnings.warn("'get_rule_parameter' is deprecated, use 'HABApp.parameters.Parameter()' instead",
                      DeprecationWarning, 2)

        assert isinstance(file_name, str), type(file_name)
        import HABApp.parameters
        return HABApp.parameters.Parameter(file_name, *keys, default_value=default_value)

    # -----------------------------------------------------------------------------------------------------------------
    # internal functions
    # -----------------------------------------------------------------------------------------------------------------
    def __get_rule_name(self, callback):
        return f'{self.rule_name}.{callback.__name__}' if self.rule_name else None

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
    def _process_events(self, now):

        # sheduled events
        clean_events = False
        for future_event in self.__future_events:  # type: OneTimeCallback
            future_event.check_due(now)
            future_event.execute()
            if future_event.is_finished:
                clean_events = True

        # remove finished events
        if clean_events:
            self.__future_events = [k for k in self.__future_events if not k.is_finished]
        return None

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
            raise RuntimeError('Could not find parent rule!')

        __vars = frm.f_locals
        depth += 1
        if 'self' in __vars:
            rule = __vars['self']
            if isinstance(rule, Rule):
                return rule
