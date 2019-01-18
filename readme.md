# HABApp
_Easy automation with openHAB and/or MQTT_
[![Build Status](https://travis-ci.org/spacemanspiff2007/HABApp.svg?branch=master)](https://travis-ci.org/spacemanspiff2007/HABApp)

HABApp is a asyncio/multithread application that connects to an openhab instance and/or a MQTT broker.
It is possible to create rules that listen to events from these instances and then react accordingly.

## Goals
The goal of this application is to provide a simple way to create home automation rules in python.
With full syntax highlighting and descriptive names it should almost never be required to look something up in the documentation

# Installation
The installation is very easy. This module can be installed through pip (or pip3 on linux):
```
pip install HABApp
```
However it is recommended to create a virtual environment, first.
Once the virtual environment is activated the habapp-command can be used to run it.

# Usage
## First start
It is recommended to specify a folder before first start.
```
python -m HABApp -c /Path/to/Config/Folder/
habapp -c /Path/to/Config/Folder/              (only in activated virtual environment)
```
This will also create some dummy configuration files:
- _config.yml_: Used to configure the behaviour of HABApp
- _logging.yml_ : Used to setup logging

## Creating rules
Create a python file in the rules directory (see _config.yml_)
This rule will automatically be reloaded when the file changes.

A simple rule could look like this
```python
import HABApp
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent

class MyRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        # Subscribe to ItemStateEvent for item TestSwitchTOGGLE
        self.listen_event( 'TestSwitchTOGGLE', self.cb, ValueUpdateEvent)

    def cb(self, event):
        assert isinstance(event, ValueUpdateEvent)  # this will provide syntax highlighting for event
        self.post_update('MyOtherItem', 'test')

MyRule()

# MQTT example
class MyMQTTRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        # Subscribe to topic but only process changes
        self.listen_event( 'test/topic1', self.cb, ValueChangeEvent)

    def cb(self, event):
        assert isinstance(event, ValueChangeEvent)
        self.mqtt_publish( 'test/topic2', event.value + 1)

MyMQTTRule()

```

More functionality is available through class functions.
It is recommended to use an editor with syntax highlighting.
Examples:
```python
# Listen for events
self.listen_event(name, callback)               # Callback on any event
self.listen_event(name, callback, even_type)    # Callback if event is instance of event_type


# Watch if items do not change a specific ammount of time and then generate an event
self.item_watch(item_name, seconds_constant, watch_only_changes = True)
# This also registers an event listener with a corresponding event
self.item_watch_and_listen(item_name, seconds_constant, callback, watch_only_changes = True)


# HAPApp item cache
# Lookups are almost instant so this can be used to get states inside of rules
self.get_item_state(item_name)
self.get_item(item_name)
self.item_exists(item_name)
self.set_item_state(item_name, value)   # If the item does not exist it will be created


# Post an event to the HABApp event bus.
# Can be used to post and react to custom events together with self.listen_event
# Also creates an item in the item cache
self.post_event(name, event)


# Interact with openhab (if configured)
self.post_update(item_name, value)
self.send_command(item_name, value)
self.create_openhab_item(item_type, item_name)
self.remove_openhab_item(item_name)


# MQTT (if configured)
# Node: subscribing is possible through the config,
#       changes to mqtt config entries get picked up without a restart
self.mqtt_publish(self, topic, payload, qos=None, retain=None)


# Time intervalls
self.run_every( date_time, interval, callback)
self.run_on_day_of_week(time, ['Mon,Tue'], callback)
self.run_on_workdays(time, callback)
self.run_on_weekends(time, callback)
self.run_daily(callback)
self.run_hourly(callback)
self.run_minutely(callback)
self.run_at(date_time, callback)
self.run_soon(callback)


# get another rule by name
self.get_rule(rule_name)
```