import asyncio
import datetime
import random
import sys
import typing

import HABApp
import HABApp.core
import HABApp.openhab.events
import HABApp.rule_manager
import HABApp.util
from .watched_item import WatchedItem


class Rule:
    def __init__(self):

        # get the variables from the caller
        __vars = sys._getframe(1).f_globals
        __runtime__ = __vars['__HABAPP__RUNTIME__']
        __rule_file__ = __vars['__HABAPP__RULE_FILE__']

        # this is a list which contains all rules of this file
        __vars['__HABAPP__RULES'].append(self)

        assert isinstance(__runtime__, HABApp.Runtime)
        self.__runtime = __runtime__

        assert isinstance(__rule_file__, HABApp.rule_manager.RuleFile)
        self.__rule_file = __rule_file__

        self.__event_listener: typing.List[HABApp.core.EventListener] = []
        self.__future_events: typing.List[HABApp.util.ScheduledCallback] = []
        self.__watched_items: typing.List[ WatchedItem] = []

        self.rule_name = ""

    def __convert_to_oh_type(self, _in):
        if isinstance(_in, datetime.datetime):
            return _in.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + self.__runtime.config.openhab.general.timezone
        return str(_in)

    def item_exists(self, item_name) -> bool:
        """
        Checks whether an item exists
        :param item_name: Name of the item
        :return: True or False
        """
        assert isinstance(item_name, str), type(item_name)
        HABApp.core.Items.item_exists(item_name)

    def item_state(self, item_name):
        """
        Return the item state
        :param item_name: Name of the item
        :return: state or None
        """
        return HABApp.core.Items.get_item(item_name).state

    def item_watch(self, item_name, seconds_constant, watch_only_changes = True) -> WatchedItem:
        assert isinstance(item_name, str)
        assert isinstance(seconds_constant, int)
        assert isinstance(watch_only_changes, bool)
        
        item = WatchedItem(
            name=item_name,
            constant_time=seconds_constant,
            watch_changes=watch_only_changes
        )
        self.__watched_items.append(item)
        return item

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

    def post_Update(self, item_name, value):
        value = self.__convert_to_oh_type(value)
        asyncio.run_coroutine_threadsafe(
            self.__runtime.openhab_connection.async_post_update(str(item_name), value),
            self.__runtime.loop
        )

    def send_Command(self, item_name, value):
        value = self.__convert_to_oh_type(value)
        asyncio.run_coroutine_threadsafe(
            self.__runtime.openhab_connection.async_send_command(str(item_name), value),
            self.__runtime.loop
        )

    def item_create(self, item_type, item_name, label="", category="", tags=[], groups=[]):
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

    def remove_item(self, item_name: str):
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
        self.run_every(start, interval, callback, *args, **kwargs)

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
        self.run_every(start, interval, callback, *args, **kwargs)

    def run_minutely(self, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        start = datetime.datetime.now() + datetime.timedelta(seconds=random.randint(0, 60 - 1))
        interval = datetime.timedelta(seconds=60)
        self.run_every(start, interval, callback, *args, **kwargs)

    def run_at(self, date_time, callback, *args, **kwargs) -> HABApp.util.ScheduledCallback:
        "Run a function at a specified date_time"
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
