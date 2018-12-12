# HABApp
_Easy automations with openHAB_

[![Build Status](https://travis-ci.org/spacemanspiff2007/HABApp.svg?branch=master)](https://travis-ci.org/spacemanspiff2007/HABApp)

## Goals

# Installation
The installation is very easy. This module can be installed through pip (or pip3 on linux):
```
pip install HABApp
```
However it is recommended to create a virtual environment, first.

# Usage
## First start
It is recommended to specify a folder before first start.
```
python -m HABApp -c /Path/to/Config/Folder/
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
from HABApp.openhab.events.item_events import ItemStateEvent

class MyRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        # Subscribe to ItemStateEvent for item TestSwitchTOGGLE
        self.listen_event( 'TestSwitchTOGGLE', self.cb, ItemStateEvent)

    def cb(self, event):
        print( f'CALLBACK: {event}')
        assert isinstance(event, ItemStateEvent)
        self.post_Update('MyOtherItem', 'test')

MyRule()
```
More functionality is available through class functions.
It is recommended to use an editor with syntax highlighting.
Examples:
```python
# Listen for events
self.listen_event(item_name, callback, None)
self.listen_event(item_name, callback, even_type)

# Interact with openhab
self.post_Update(item_name, value)
self.send_Command(item_name, value)
self.item_exists(item_name)
self.item_state(item_name)
self.item_create(item_type, item_name)
self.remove_item(item_name)

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