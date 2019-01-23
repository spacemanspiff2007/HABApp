import asyncio
import datetime
import random
import sys
import typing
import logging

import HABApp
import HABApp.core
import HABApp.openhab.events
import HABApp.rule_manager
import HABApp.util
import HABApp.classes
from .watched_item import WatchedItem

log = logging.getLogger('HABApp.Rule')


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

        # this is a list which contains all rules of this file
        __vars['__HABAPP__RULES'].append(self)

        assert isinstance(__runtime__, HABApp.Runtime)
        self.__runtime = __runtime__

        assert isinstance(__rule_file__, HABApp.rule_manager.RuleFile)
        self.__rule_file = __rule_file__

        self.__event_listener: typing.List[HABApp.core.EventListener] = []
        self.__future_events: typing.List[HABApp.util.ScheduledCallback] = []
        self.__watched_items: typing.List[ WatchedItem] = []

        # so the user can set this before calling __init__
        if not hasattr(self, 'rule_name'):
            self.rule_name = ""

    def __convert_to_oh_type(self, _in):
        if isinstance(_in, datetime.datetime):
            return _in.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + self.__runtime.config.openhab.general.timezone
        elif isinstance(_in, HABApp.core.Item):
            return str(_in.state)
        elif isinstance(_in, HABApp.classes.Color):
            return f'{_in.hue:.1f},{_in.saturation:.1f},{_in.value:.1f}'

        return str(_in)

    def item_exists(self, item_name) -> bool:
        """
        Checks whether an item exists
        :param item_name: Name of the item
        :return: True or False
        """
        assert isinstance(item_name, str), type(item_name)
        return HABApp.core.Items.item_exists(item_name)

    def get_item_state(self, item_name, default=None):
        """
        Return the state of the item.
        :param item_name:
        :param default: If the item does not exist or is None this value will be returned (has to be != None)
        :return: state of the specified item
        """
        if default is None:
            return HABApp.core.Items.get_item(item_name).state

        try:
            state = HABApp.core.Items.get_item(item_name).state
        except KeyError:
            return default

        if state is None:
            return default
        return state

    def set_item_state(self, item_name, value):
        assert isinstance(item_name, str)

        try:
            old_state = HABApp.core.Items.get_item(item_name).state
        except KeyError:
            old_state = None

        self.post_event(item_name, HABApp.core.ValueUpdateEvent(name=item_name, value=value))
        if old_state != value:
            self.post_event(item_name, HABApp.core.ValueChangeEvent(name=item_name, value=value, old_value=old_state))
        return None

    def item_watch(self, item_name, seconds_constant, watch_only_changes = True) -> WatchedItem:
        assert isinstance(item_name, str)
        assert isinstance(seconds_constant, int)
        assert isinstance(watch_only_changes, bool)

        item = WatchedItem(
            name=item_name,
            constant_time=seconds_constant,
            watch_only_changes=watch_only_changes
        )
        self.__watched_items.append(item)
        return item

    def item_watch_and_listen(self, item_name, seconds_constant, callback,
                              watch_only_changes = True) -> typing.Tuple[WatchedItem, HABApp.core.EventListener]:

        watched_item = self.item_watch(item_name, seconds_constant, watch_only_changes)
        event_listener = self.listen_event(
            item_name,
            callback,
            HABApp.core.ValueNoChangeEvent if watch_only_changes else HABApp.core.ValueNoUpdateEvent
        )
        return watched_item, event_listener

    def get_item(self, item_name) -> HABApp.core.Item:
        return HABApp.core.Items.get_item(item_name)

    def post_event(self, name, event):
        """
        Post an Event to the Event Bus
        :param name: name to post event to
        :param event: Event class to be used (must be class instance)
        :return:
        """
        assert isinstance(name, str), type(name)
        return HABApp.core.Events.post_event(name, event)

    def listen_event(self, name: str, callback, even_type=None) -> HABApp.core.EventListener:
        """
        Register and event listener
        :param name: name to listen to
        :param callback: callback
        :param even_type: None for all events, class to only make a call on class instances
        :return: Instance of EventListener
        """
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        listener = HABApp.core.EventListener(name, cb, even_type)
        self.__event_listener.append(listener)
        HABApp.core.Events.add_listener(listener)
        return listener

    def post_update(self, item_name, value):
        value = self.__convert_to_oh_type(value)
        asyncio.run_coroutine_threadsafe(
            self.__runtime.openhab_connection.async_post_update(str(item_name), value),
            self.__runtime.loop
        )

    def send_command(self, item_name, value):
        value = self.__convert_to_oh_type(value)
        asyncio.run_coroutine_threadsafe(
            self.__runtime.openhab_connection.async_send_command(str(item_name), value),
            self.__runtime.loop
        )

    def create_openhab_item(self, item_type, item_name, label="", category="", tags=[], groups=[]):
        """

        :param item_type:
        :param item_name:
        :param label:
        :param category:
        :param tags:
        :param groups:
        :return: True if Successfull else False
        """
        assert isinstance(item_type, str), type(item_type)
        item_type = item_type.title()
        assert item_type in ['String', 'Number', 'Switch', 'Contact', 'Color', 'Contact'], item_type
        assert isinstance(item_name, str), type(item_name)
        assert isinstance(label, str), type(label)
        assert isinstance(category, str), type(category)
        assert isinstance(tags, list), type(tags)
        assert isinstance(groups, list), type(groups)

        future = asyncio.run_coroutine_threadsafe(
            self.__runtime.openhab_connection.async_create_item(item_type, item_name, label, category, tags, groups),
            self.__runtime.loop
        )

        return future.result(self.__runtime.config.async_timeout)

    def remove_openhab_item(self, item_name: str):
        assert isinstance(item_name, str), type(item_name)
        future = asyncio.run_coroutine_threadsafe(
            self.__runtime.openhab_connection.async_remove_item(item_name),
            self.__runtime.loop
        )
        return future.result(self.__runtime.config.async_timeout)

    def run_every(self, date_time, interval, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        """
        Run a function every interval
        :param date_time:
        :param interval:
        :param callback:
        :param args:
        :param kwargs:
        :return:
        """
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.ReoccuringScheduledCallback(date_time, interval, cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_on_day_of_week(self, time, weekdays, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:

        # names of weekdays in local language
        lookup = {datetime.date(2001, 1, i).strftime('%A'): i for i in range(1, 8)}
        lookup.update( {datetime.date(2001, 1, i).strftime('%A')[:3]: i for i in range(1, 8)})

        # abreviations in German and English
        lookup.update({"Mo": 1, "Di": 2, "Mi": 3, "Do": 4, "Fr": 5, "Sa": 6, "So": 7})
        lookup.update({"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7})
        lookup = {k.lower(): v for k, v in lookup.items()}

        if isinstance(weekdays, int) or isinstance(weekdays, str):
            weekdays = [weekdays]
        for i, val in enumerate(weekdays):
            if not isinstance(val, str):
                continue
            weekdays[i] = lookup[val.lower()]

        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.DayOfWeekScheduledCallback(time, weekdays, cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_on_every_day(self, time, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.DayOfWeekScheduledCallback(time, [1, 2, 3, 4, 5, 6, 7], cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_on_workdays(self, time, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.WorkdayScheduledCallback(time, cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_on_weekends(self, time, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.WeekendScheduledCallback(time, cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_daily(self, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        """
        Picks a random minute and second and runs the callback every hour
        :param callback:
        :param args:
        :param kwargs:
        :return:
        """
        start = datetime.datetime.now() + datetime.timedelta(seconds=random.randint(0, 24 * 3600 - 1))
        interval = datetime.timedelta(days=1)
        return self.run_every(start, interval, callback, *args, **kwargs)

    def run_hourly(self, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        """
        Picks a random minute and second and runs the callback every hour
        :param callback:
        :param args:
        :param kwargs:
        :return:
        """
        start = datetime.datetime.now() + datetime.timedelta(seconds=random.randint(0, 3600 - 1))
        interval = datetime.timedelta(seconds=3600)
        return self.run_every(start, interval, callback, *args, **kwargs)

    def run_minutely(self, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        start = datetime.datetime.now() + datetime.timedelta(seconds=random.randint(0, 60 - 1))
        interval = datetime.timedelta(seconds=60)
        return self.run_every(start, interval, callback, *args, **kwargs)

    def run_at(self, date_time, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        "Run a function at a specified date_time"
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.ScheduledCallback(date_time, cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_in(self, seconds, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        """Run a function in x seconds"""
        assert isinstance(seconds, int), f'{seconds} ({type(seconds)})'
        date_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)

        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.ScheduledCallback(date_time, cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def run_soon(self, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        """
        Run the callback as soon as possible (typically in the next second).
        :param callback:    function to call
        :param args:    args for the callback
        :param kwargs:  kwargs for the callback
        :return:
        """
        cb = HABApp.util.WorkerRuleWrapper(callback, self)
        future_event = HABApp.util.ScheduledCallback(datetime.datetime.now(), cb, *args, **kwargs)
        self.__future_events.append(future_event)
        return future_event

    def get_rule(self, rule_name):  # todo: einkommentieren mit python3.7 -> Rule:
        assert isinstance(rule_name, str), type(rule_name)
        return self.__runtime.rule_manager.get_rule(rule_name)

    def mqtt_publish(self, topic, payload=None, qos=None, retain=None):
        assert isinstance(topic, str), type(str)
        self.__runtime.mqtt_connection.publish(topic, payload, qos, retain)

    @HABApp.util.PrintException
    def _check_rule(self):
        # Check if item exists
        if not HABApp.core.Items.items:
            return None

        for item in self.__event_listener:
            if not HABApp.core.Items.item_exists(item.name):
                log.warning(f'Item "{item.name}" does not exist (yet)! '
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
        for future_event in self.__future_events:  # type: HABApp.util.ScheduledCallback
            future_event.check_due(now)
            future_event.execute(HABApp.core.Workers)
            if future_event.is_finished:
                clean_events = True

        # remove finished events
        if clean_events:
            self.__future_events = [k for k in self.__future_events if not k.is_finished]
        return None

    @HABApp.util.PrintException
    def _cleanup(self):
        for listener in self.__event_listener:
            HABApp.core.Events.remove_listener(listener)

        for event in self.__future_events:
            event.cancel()
        self.__future_events.clear()

        self.__watched_items.clear()
