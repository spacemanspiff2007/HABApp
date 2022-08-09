# HABApp
![Tests Status](https://github.com/spacemanspiff2007/HABApp/workflows/Tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/habapp/badge/?version=latest)](https://habapp.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/HABApp/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/HABApp/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/habapp)

![PyPI](https://img.shields.io/pypi/v/HABapp)
[![Downloads](https://pepy.tech/badge/habapp/month)](https://pepy.tech/project/habapp)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/spacemanspiff2007/habapp?label=docker)
![Docker Pulls](https://img.shields.io/docker/pulls/spacemanspiff2007/habapp)


_Easy automation with MQTT and/or openHAB_


HABApp is a asyncio/multithread application that connects to an openHAB instance and/or a MQTT broker.
It is possible to create rules that listen to events from these instances and then react accordingly.

## Goals
The goal of this application is to provide a simple way to create home automation rules in python.
With full syntax highlighting and descriptive names it should almost never be required to look something up in the documentation

## Documentation
[The documentation can be found at here](https://habapp.readthedocs.io)

## Examples

### MQTT Rule example
```python
import datetime
import random

import HABApp
from HABApp.mqtt.items import MqttItem
from HABApp.core.events import ValueChangeEvent, ValueChangeEventFilter, ValueUpdateEvent, ValueUpdateEventFilter


class ExampleMqttTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        self.run.every(
            start_time=datetime.timedelta(seconds=60),
            interval=datetime.timedelta(seconds=30),
            callback=self.publish_rand_value
        )

        # this will trigger every time a message is received under "test/test"
        self.listen_event('test/test', self.topic_updated, ValueUpdateEventFilter())

        # This will create an item which will store the payload of the topic so it can be accessed later.
        self.item = MqttItem.get_create_item('test/value_stored')
        # Since the payload is now stored we can trigger only if the value has changed
        self.item.listen_event(self.item_topic_updated, ValueChangeEventFilter())

    def publish_rand_value(self):
        print('test mqtt_publish')
        self.mqtt.publish('test/test', str(random.randint(0, 1000)))

    def topic_updated(self, event: ValueUpdateEvent):
        assert isinstance(event, ValueUpdateEvent), type(event)
        print( f'mqtt topic "test/test" updated to {event.value}')

    def item_topic_updated(self, event: ValueChangeEvent):
        print(self.item.value)  # will output the current item value
        print( f'mqtt topic "test/value_stored" changed from {event.old_value} to {event.value}')


ExampleMqttTestRule()
```

### openHAB rule example

```python
import HABApp
from HABApp.core.events import ValueUpdateEvent, ValueChangeEvent, ValueChangeEventFilter, ValueUpdateEventFilter
from HABApp.openhab.events import ItemCommandEvent, ItemStateEventFilter, ItemCommandEventFilter, \
  ItemStateChangedEventFilter


class MyOpenhabRule(HABApp.Rule):

  def __init__(self):
    super().__init__()

    # Trigger on item updates
    self.listen_event('TestContact', self.item_state_update, ItemStateEventFilter())
    self.listen_event('TestDateTime', self.item_state_update, ValueUpdateEventFilter())

    # Trigger on item changes
    self.listen_event('TestDateTime', self.item_state_change, ItemStateChangedEventFilter())
    self.listen_event('TestSwitch', self.item_state_change, ValueChangeEventFilter())

    # Trigger on item commands
    self.listen_event('TestSwitch', self.item_command, ItemCommandEventFilter())

  def item_state_update(self, event: ValueUpdateEvent):
    assert isinstance(event, ValueUpdateEvent)
    print(f'{event}')

  def item_state_change(self, event: ValueChangeEvent):
    assert isinstance(event, ValueChangeEvent)
    print(f'{event}')

    # interaction is available through self.openHAB or self.oh
    self.openhab.send_command('TestItemCommand', 'ON')

  def item_command(self, event: ItemCommandEvent):
    assert isinstance(event, ItemCommandEvent)
    print(f'{event}')

    # interaction is available through self.openhab or self.oh
    self.oh.post_update('TestItemUpdate', 123)


MyOpenhabRule()
```

# Changelog
#### 1.0.3 (09.08.2022)
- OpenHAB Thing can now be enabled/disabled with ``thing.set_enabled()``
- ClientID for MQTT should now be unique for every HABApp installation
- Reworked MultiModeItem, now a default value is possible when no mode is active
- Added some type hints and updated documentation

#### 1.0.2 (29.07.2022)
- Fixed setup issues
- Fixed unnecessary long tracebacks

#### 1.0.1 (25.07.2022)
- Dockerfile is Python 3.10 and non slim

#### 1.0.0 (25.07.2022)
- OpenHAB >= 3.3 and Python >= 3.8 only!
- Major internal refactoring
- Startup issues are gone with a new and improved connection mechanism.
- New configuration library: More settings can be configured in the configuration file.
  Config values are also described in the docs. Also better error messages (hopefully)
- Improved event log performance (``BufferEventFile`` no longer needed and should be removed)
- Improved openhab performance (added some buffers)
- Improved mqtt performance
- Better tracebacks in case of error
- EventFilters can be logically combined ("and", "or") so rules trigger only once
- Label, Groups and Metadata is part of the OpenhabItem and can easily be accessed
- Added possibility to run arbitrary user code before the HABApp configuration is loaded
- Fixed setup issues
- Fixed some known bugs and introduced new ones ;-)
- Docker file changed to a multi stage build. Mount points changed to ``/habapp/config``.

**Migration to new version**


``self.listen_event`` now requires an instance of EventFilter.

Old:
```python
from HABApp.core.events import ValueUpdateEvent
...
self.my_sensor = Item.get_item('my_sensor')
self.my_sensor.listen_event(self.movement, ValueUpdateEvent)
```

New:
```python
from HABApp.core.events import ValueUpdateEventFilter
...
self.my_sensor = Item.get_item('my_sensor')
self.my_sensor.listen_event(self.movement, ValueUpdateEventFilter())   # <-- Instance of EventFilter
```

```text
HABApp:
  ValueUpdateEvent -> ValueUpdateEventFilter()
  ValueChangeEvent -> ValueChangeEventFilter()

Openhab:
  ItemStateEvent        -> ItemStateEventFilter()
  ItemStateChangedEvent -> ItemStateChangedEventFilter()
  ItemCommandEvent      -> ItemCommandEventFilter()

MQTT:
  MqttValueUpdateEvent -> MqttValueUpdateEventFilter()
  MqttValueChangeEvent -> MqttValueChangeEventFilter()
```

**Migration to new docker image**
- change the mount point of the config from ``/config`` to ``/habapp/config``
- The new image doesn't run as root. You can set `USER_ID` and `GROUP_ID` to the user you want habapp to run with. It's necessary to modify the permissions of the mounted folder accordingly.

---

#### 0.31.2 (17.12.2021)
- Added command line switch to display debug information
- Display debug information on missing dependencies
- Added a small splash screen when HABApp is started
- May doc updates
- Reworked EventListenerGroup

#### 0.31.1 (29.10.2021)
- Added support for item metadata
- Added possibility to search for items by metadata
- Added EventListenerGroup to subscribe/cancel multiple listeners at once

#### 0.31.0 (08.10.2021)
- added self.get_items to easily search for items in a rule
- added full support for tags and groups on OpenhabItem
- Application should now properly shut down when there is a PermissionError
- Added DatetimeItem to docs
- Label in commandOption is optional
- Added message when file is removed
- Examples in the docs get checked with a newly created sphinx extension
- Reworked the openHAB tests

#### 0.30.3 (17.06.2021)
- add support for custom ca cert for MQTT
- Scheduler runs only when the rule file has been loaded properly
- Sync openHAB calls raise an error when called from an async context
- Replaced thread check for asyncio with a contextvar (internal)

#### 0.30.3 (01.06.2021)
- Scheduler runs only when the rule file has been loaded properly
- Replaced thread check for asyncio with a contextvar
- Sync openHAB calls raise an error when called from an async context

#### 0.30.2 (26.05.2021)
- Item and Thing loading from openHAB is more robust and disconnects now properly if openHAB is only partly ready
- Renamed command line argument "-s" to "-wos" or "--wait_os_uptime"
- Updated dependencies

#### 0.30.1 (07.05.2021)
- latitude is now set correctly for sunrise/sunset calculation (closes #217)
- Added missing " for tags in textual thing configuration
- Updated scheduler which fixes an overflow error(#216)
- States of openHAB groups are now unpacked correctly

#### 0.30.0 (02.05.2021)

Attention:
- No more support for python 3.6!
- Migration of rules is needed!

Changelog
- Switched to Apache2.0 License
- Fix DateTime string parsing for OH 3.1 (#214)
- State of Groupitem gets set correctly
- About ~50% performance increase for async calls in rules
- Significantly less CPU usage when no functions are running
- Completely reworked the file handling (loading and dependency resolution)
- Completely reworked the Scheduler!
  - Has now subsecond accuracy (finally!)
  - Has a new .countdown() job which can simplify many rules.
    It is made for functions that do something after a certain period of time (e.g. switch a light off after movement)
- Added hsb_to_rgb, rgb_to_hsb functions which can be used in rules
- Better error message if configured foldes overlap with HABApp folders
- Renamed HABAppError to HABAppException
- Some Doc improvements

Migration of rules:
- Search for ``self.run_`` and replace with ``self.run.``
- Search for ``self.run.in`` and replace with ``self.run.at``
- Search for ``.get_next_call()`` and replace with ``.get_next_run()`` (But make sure it's a scheduled job)
- Search for ``HABAppError`` and replace with ``HABAppException``


#### 0.20.2 (07.04.2021)
- Added HABApp.util.functions with min/max
- Reworked small parts of the file watcher
- Doc improvements
- Dependency updates
