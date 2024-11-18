# HABApp
![Tests Status](https://github.com/spacemanspiff2007/HABApp/workflows/Tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/habapp/badge/?version=latest)](https://habapp.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/HABApp/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/HABApp/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/habapp)

![PyPI](https://img.shields.io/pypi/v/HABapp)
[![Downloads](https://static.pepy.tech/badge/habapp/month)](https://pepy.tech/project/habapp)
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

## Help out
HABApp was created for my own use, but I wanted others to profit from it, too.
Creating, maintaining and developing it takes a lot of time.
If you think this is a great tool and want to support it you can donate,
so I can buy some more coffee to keep development going. :wink:

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-informational?logo=paypal)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YU5U9YQN56JVA)

All donations are greatly appreciated!


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
from HABApp.openhab.events import ItemCommandEvent, ItemStateUpdatedEventFilter, ItemCommandEventFilter, \
  ItemStateChangedEventFilter


class MyOpenhabRule(HABApp.Rule):

  def __init__(self):
    super().__init__()

    # Trigger on item updates
    self.listen_event('TestContact', self.item_state_update, ItemStateUpdatedEventFilter())
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
#### 24.XX.XX (2024-XX-XX)
This is a breaking change!

Changelog:
- Switched to new scheduler
- Added ``ValueCommandEvent``. The openhab command event inherits from this event.

Migration of rules:
- Search for ``self.run.at`` and replace with ``self.run.once``
- If you use job.offset, job.earliest, job.latest or job.jitter you have to rewrite the condition to the new syntax:
  ``self.run.on_sunrise(self.my_function).offset(timedelta(hours=2))`` becomes
  ``self.run.at(self.run.trigger.sunrise().offset(timedelta(hours=2)), self.my_function)``
- All other scheduler functions will emit deprecation warnings with a hint how to rewrite them
- ``item.last_update`` and ``item.last_change`` can now directly used to check if it's newer/older than a delta.
  Replace ``item.last_update > datetime_obj`` with ``item.last_update > timedelta_obj`` or
  ``item.last_update.newer_than(minutes=10)``

#### 24.08.1 (2024-08-02)
- Fixed a possible infinite loop during thing re-sync

#### 24.08.0 (2024-08-01)
- Fixed an issue with thing re-sync
- Updated number parsing logic
- ``ItemTimeSeriesEvent`` gets ignored
- Removed verbose error messages when openHAB server disconnects
- Updated dependencies
- Reformatted some files

#### 24.02.0 (2024-02-14)
- For openHAB >= 4.1 it's possible to wait for a minimum openHAB uptime before connecting (defaults to 60s)
- Renamed config entry mqtt.connection.client_id to identifier (backwards compatible)
- ``ItemTimeSeriesUpdatedEvent`` gets ignored
- Updated dependencies
- Updated docs

#### 24.01.0 (2024-01-08)
- Added HABApp.util.RateLimiter
- Added CompressedMidnightRotatingFileHandler
- Updated dependencies
- Small improvement for RGB and HSB types
- Small improvements for openHAB items
- Added toggle for SwitchItem

#### 23.11.0 (2023-11-23)
- Fix for very small float values (#425)
- Fix for writing to persistence (#424)
- Updated dependencies

#### 23.09.2 (2023-09-24)
- Made channel type on a ``Thing`` optional (#416)
- Fixed an issue with mqtt publish and reconnect

#### 23.09.1 (2023-09-18)
- Log a warning for broken links between items and things
- Fix CI

#### 23.09.0 (2023-09-12)
- Switched version number scheme to CalVer (Calendar Versioning): ``YEAR.MONTH.COUNTER``
- Fail fast when a value instead of a callback is passed to the event listener / scheduler
- Completely removed types and type hints from traceback
- Completely reworked connection logic for openHAB and mqtt
- Added support for transformations
- Updated dependencies:
  - Improved performance
  - Support for docker secrets and environment variables in the config file
- Support sending scheduler datetimes to an item
- Search in the docs finally works again
- Updated dependencies

#### 1.1.2 (2023-06-19)
- Re-added `ItemStateEventFilter`
- Improved parsing of `DateTime` values

#### 1.1.1 (2023-06-16)
- Fixed a bug where the rule context was not found

#### 1.1.0 (2023-06-15)
This is a breaking change!
- Renamed `GroupItemStateChangedEvent` to `GroupStateChangedEvent`
- Groups issue a `GroupStateUpdateEvent` when the state updates on OH3 (consistent with OH4 behavior)
- Groups work now with `ValueUpdateEvent` and `ValueChangedEvent` as expected
- ~~Renamed `ItemStateEvent` to `ItemStateUpdatedEvent`~~
- Ignored ItemStateEvent on OH4
- Fewer warnings for long-running functions (execution of <FUNC_NAME> took too long)
- `Thing` status and status_detail are now an Enum
- Added `status_detail` to `Thing`
- `LocationItem` now provides the location as a tuple
- Added support for `Point` events
- Improved item sync from openHAB (no more false item state `None` after startup)
- Improved startup behavior when openHAB and HABApp get started together (e.g. after reboot)
- Fixed an issue with short tracebacks for HABApp internal files
- Doc improvements

#### 1.0.8 (2023-02-09)
- Fixed an issue when using token based authentication with openHAB
- Fixed an issue with the asyncio event loop under Python < 3.10

#### 1.0.7 (2023-02-09)
- ``ContactItem`` has ``open()``/``closed()`` methods
- Setting persistence values now works for some persistence services
- Don't connect when user/password is missing for openHAB

#### 1.0.6 (2022-11-08)
- Added log message if item for ping does not exist
- Added ``execute_python`` and reworked ``execute_subprocess``:
  HABApp will now by default pass only the captured output as a str into the callback.
- Reworked ``Thing`` handling

#### 1.0.5 (2022-10-20)
- Added new item function ``post_value_if`` and ``oh_post_update_if`` to conditionally update an item
- Added support for new alive event with openHAB 3.4
- Reworked file writer for textual thing config
- Added support for ThingConfigStatusInfoEvent
- MultiModeValue returns True/False if item value was changed
- Updated dependencies

#### 1.0.4 (2022-08-25)
- New RGB & HSB datatype for simpler color handling
- Fixed Docker build
- Bugfixes

#### 1.0.3 (2022-08-09)
- OpenHAB Thing can now be enabled/disabled with ``thing.set_enabled()``
- ClientID for MQTT should now be unique for every HABApp installation
- Reworked MultiModeItem, now a default value is possible when no mode is active
- Added some type hints and updated documentation

#### 1.0.2 (2022-07-29)
- Fixed setup issues
- Fixed unnecessary long tracebacks

#### 1.0.1 (2022-07-25)
- Dockerfile is Python 3.10 and non slim

#### 1.0.0 (2022-07-25)
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

#### 0.31.2 (2021-12-17)
- Added command line switch to display debug information
- Display debug information on missing dependencies
- Added a small splash screen when HABApp is started
- May doc updates
- Reworked EventListenerGroup

#### 0.31.1 (2021-10-29)
- Added support for item metadata
- Added possibility to search for items by metadata
- Added EventListenerGroup to subscribe/cancel multiple listeners at once

#### 0.31.0 (2021-10-08)
- added self.get_items to easily search for items in a rule
- added full support for tags and groups on OpenhabItem
- Application should now properly shut down when there is a PermissionError
- Added DatetimeItem to docs
- Label in commandOption is optional
- Added message when file is removed
- Examples in the docs get checked with a newly created sphinx extension
- Reworked the openHAB tests

#### 0.30.3 (2021-06-17)
- add support for custom ca cert for MQTT
- Scheduler runs only when the rule file has been loaded properly
- Sync openHAB calls raise an error when called from an async context
- Replaced thread check for asyncio with a contextvar (internal)

#### 0.30.3 (2021-06-01)
- Scheduler runs only when the rule file has been loaded properly
- Replaced thread check for asyncio with a contextvar
- Sync openHAB calls raise an error when called from an async context

#### 0.30.2 (2021-05-26)
- Item and Thing loading from openHAB is more robust and disconnects now properly if openHAB is only partly ready
- Renamed command line argument "-s" to "-wos" or "--wait_os_uptime"
- Updated dependencies

#### 0.30.1 (2021-05-07)
- latitude is now set correctly for sunrise/sunset calculation (closes #217)
- Added missing " for tags in textual thing configuration
- Updated scheduler which fixes an overflow error(#216)
- States of openHAB groups are now unpacked correctly

#### 0.30.0 (2021-05-02)

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


#### 0.20.2 (2021-04-07)
- Added HABApp.util.functions with min/max
- Reworked small parts of the file watcher
- Doc improvements
- Dependency updates
