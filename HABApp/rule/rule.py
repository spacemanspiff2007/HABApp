import asyncio
import datetime
import logging
import random
import sys
import traceback
import typing
import warnings

import HABApp
import HABApp.core
import HABApp.openhab
import HABApp.rule_manager
import HABApp.util
from HABApp.core.events import AllEvents
from .interfaces import async_subprocess_exec
from .scheduler import ReoccurringScheduledCallback, OneTimeCallback, DayOfWeekScheduledCallback, \
    TYPING_DATE_TIME, SunScheduledCallback
from .watched_item import WatchedItem

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
        self.__future_events: typing.List[OneTimeCallback] = []
        self.__watched_items: typing.List[WatchedItem] = []
        self.__unload_functions: typing.List[typing.Callable[[], None]] = []

        # schedule cleanup
        self.register_on_unload(self.__cleanup_rule)


        # suggest a rule name if it is not
        self.rule_name: str = self.__rule_file.suggest_rule_name(self)

        # interfaces
        self.async_http: HABApp.rule.interfaces.AsyncHttpConnection = self.__runtime.async_http if not test else None
        self.mqtt = self.__runtime.mqtt_connection.interface if not test else None
        self.oh: HABApp.openhab.OpenhabInterface = HABApp.openhab.get_openhab_interface() if not test else None
        self.openhab: HABApp.openhab.OpenhabInterface = self.oh

    def __cleanup_rule(self):
        # Important: set the dicts to None so we don't schedule a future event during _cleanup.
        # If dict is set to None we will crash instead but it is no problem because everything gets unloaded anyhow
        event_listeners = self.__event_listener
        future_events = self.__future_events

        self.__event_listener = None
        self.__future_events = None
        self.__watched_items = None

        # Actually remove the listeners/events
        for listener in event_listeners:
            HABApp.core.EventBus.remove_listener(listener)

        for event in future_events:
            event.cancel()
        return None


    def item_watch(self, name: typing.Union[str, HABApp.core.items.Item],
                   seconds_constant: int, watch_only_changes=True) -> WatchedItem:
        """
        | Keep watch on the state of an item.
        | if `watch_only_changes` is True (default) and the state does not change for `seconds_constant` a
          `ValueNoChangeEvent` will be sent to the event bus.
        | if `watch_only_changes` is False and the state does not receive and update for `seconds_constant` a
          `ValueNoUpdateEvent` will be sent to the event bus.

        :param name: item name or item that shall be watched
        :param seconds_constant: the amount of seconds the item has to be constant or has not received an update
        :param watch_only_changes:
        """
        assert isinstance(name, (str, HABApp.core.items.Item)), type(name)
        assert isinstance(seconds_constant, int)
        assert isinstance(watch_only_changes, bool)

        item = WatchedItem(
            name=name.name if isinstance(name, HABApp.core.items.Item) else name,
            constant_time=seconds_constant,
            watch_only_changes=watch_only_changes
        )
        self.__watched_items.append(item)
        return item

    def item_watch_and_listen(self, name: typing.Union[HABApp.core.items.Item, str], seconds_constant: int, callback,
                              watch_only_changes=True) -> typing.Tuple[WatchedItem, HABApp.core.EventBusListener]:
        """
        Convenience function which combines :class:`~HABApp.Rule.item_watch` and :class:`~HABApp.Rule.listen_event`

        :param name: item name
        :param seconds_constant:
        :param callback: callback that accepts one parameter which will contain the event
        :param watch_only_changes:
        :return:
        """

        watched_item = self.item_watch(name, seconds_constant, watch_only_changes)
        event_listener = self.listen_event(
            name,
            callback,
            HABApp.core.events.ValueNoChangeEvent if watch_only_changes else HABApp.core.events.ValueNoUpdateEvent
        )
        return watched_item, event_listener

    def post_event(self, name, event):
        """
        Post an event to the event bus

        :param name: name or item to post event to
        :param event: Event class to be used (must be class instance)
        :return:
        """
        assert isinstance(name, (str, HABApp.core.items.Item)), type(name)
        return HABApp.core.EventBus.post_event(name.name if isinstance(name, HABApp.core.items.Item) else name, event)

    def listen_event(self, name: typing.Union[HABApp.core.items.Item, str, None], callback,
                     even_type: typing.Union[AllEvents, typing.Any] = AllEvents
                     ) -> HABApp.core.EventBusListener:
        """
        Register an event listener

        :param name: item or name to listen to. Use None to listen to all events
        :param callback: callback that accepts one parameter which will contain the event
        :param even_type: Event filter. This is typically :class:`~HABApp.core.ValueUpdateEvent` or
            :class:`~HABApp.core.ValueChangeEvent` which will also trigger on changes/update from openhab
            or mqtt.
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        listener = HABApp.core.EventBusListener(
            name.name if isinstance(name, HABApp.core.items.Item) else name, cb, even_type
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
            self.__runtime.loop  # this has to be passed because we will not call it from the main thread
        )

    def run_every(self, time: TYPING_DATE_TIME, interval, callback, *args, **kwargs) -> ReoccurringScheduledCallback:
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
        future_event.set_next_run_time(time)
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
        future_event.update_run_time()
        self.__future_events.append(future_event)
        return future_event

    def run_on_day_of_week(self,
                           time: TYPING_DATE_TIME, weekdays, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: |param_scheduled_time|
        :param weekdays:
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """

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
        future_event.set_next_run_time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_on_every_day(self, time: TYPING_DATE_TIME, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: |param_scheduled_time|
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays([1, 2, 3, 4, 5, 6, 7])
        future_event.set_next_run_time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_on_workdays(self, time: TYPING_DATE_TIME, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: |param_scheduled_time|
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays('workday')
        future_event.set_next_run_time(time)
        self.__future_events.append(future_event)
        return future_event

    def run_on_weekends(self, time: TYPING_DATE_TIME, callback, *args, **kwargs) -> DayOfWeekScheduledCallback:
        """

        :param time: |param_scheduled_time|
        :param callback: |param_scheduled_cb|
        :param args: |param_scheduled_cb_args|
        :param kwargs: |param_scheduled_cb_kwargs|
        """
        cb = HABApp.core.WrappedFunction(callback, name=self.__get_rule_name(callback))
        future_event = DayOfWeekScheduledCallback(cb, *args, **kwargs)
        future_event.weekdays('weekend')
        future_event.set_next_run_time(time)
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
        future_event.set_next_run_time(date_time)
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
        future_event.set_next_run_time(fut)
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
        future_event.set_next_run_time(None)
        self.__future_events.append(future_event)
        return future_event

    def get_rule(self, rule_name: str) -> 'typing.Union[Rule, typing.List[Rule]]':
        assert rule_name is None or isinstance(rule_name, str), type(rule_name)
        return self.__runtime.rule_manager.get_rule(rule_name)

    def register_on_unload(self, func):
        """Register a function with no parameters which will be called when the rule is unloaded.
        Use this for custom cleanup functions.

        :param func: function which will be called
        """
        assert callable(func)
        assert func not in self.__unload_functions, 'Function was already registered!'
        self.__unload_functions.append(func)

    # -----------------------------------------------------------------------------------------------------------------
    # deprecated functions
    # -----------------------------------------------------------------------------------------------------------------
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

    @HABApp.util.PrintException
    def _check_rule(self):

        # Check if items do exists
        if not HABApp.core.Items.get_all_items():
            return None

        for listener in self.__event_listener:
            # Listener listens to all changes
            if listener.topic is None:
                continue

            # check if specific item exists
            if not HABApp.core.Items.item_exists(listener.topic):
                log.warning(f'Item "{listener.topic}" does not exist (yet)! '
                            f'self.listen_event in "{self.rule_name}" may not work as intended.')

        for item in self.__watched_items:
            if not HABApp.core.Items.item_exists(item.name):
                log.warning(f'Item "{item.name}" does not exist (yet)! '
                            f'self.item_watch in "{self.rule_name}" may not work as intended.')

    @HABApp.util.PrintException
    def _process_events(self, now):

        # watch items
        clean_items = False
        for item in self.__watched_items:
            item.check(now)
            if item.is_canceled:
                clean_items = True
        if clean_items:
            self.__watched_items = [k for k in self.__watched_items if not k.is_canceled]

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

    @HABApp.util.PrintException
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

                log.error( f'Error{name} while unloading "{self.rule_name}": {e}')

                # log traceback
                lines = traceback.format_exc().splitlines()
                del lines[1:3]  # see implementation in wrappedfunction.py why we do this
                for line in lines:
                    log.error(line)
