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


HABApp is a asyncio/multithread application that connects to an openhab instance and/or a MQTT broker.
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
from HABApp.core.events import ValueUpdateEvent


class ExampleMqttTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        self.run.every(
            time=datetime.timedelta(seconds=60),
            interval=datetime.timedelta(seconds=30),
            callback=self.publish_rand_value
        )

        self.listen_event('test/test', self.topic_updated, ValueUpdateEvent)

    def publish_rand_value(self):
        print('test mqtt_publish')
        self.mqtt.publish('test/test', str(random.randint(0, 1000)))

    def topic_updated(self, event):
        assert isinstance(event, ValueUpdateEvent), type(event)
        print( f'mqtt topic "test/test" updated to {event.value}')


ExampleMqttTestRule()
```

### Openhab rule example
```python
import HABApp
from HABApp.core.events import ValueUpdateEvent, ValueChangeEvent
from HABApp.openhab.events import ItemStateEvent, ItemCommandEvent, ItemStateChangedEvent

class MyOpenhabRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        # Trigger on item updates
        self.listen_event( 'TestContact', self.item_state_update, ItemStateEvent)
        self.listen_event( 'TestDateTime', self.item_state_update, ValueUpdateEvent)

        # Trigger on item changes
        self.listen_event( 'TestDateTime', self.item_state_change, ItemStateChangedEvent)
        self.listen_event( 'TestSwitch', self.item_state_change, ValueChangeEvent)

        # Trigger on item commands
        self.listen_event( 'TestSwitch', self.item_command, ItemCommandEvent)

    def item_state_update(self, event):
        assert isinstance(event, ValueUpdateEvent)
        print( f'{event}')

    def item_state_change(self, event):
        assert isinstance(event, ValueChangeEvent)
        print( f'{event}')

        # interaction is available through self.openhab or self.oh
        self.openhab.send_command('TestItemCommand', 'ON')

    def item_command(self, event):
        assert isinstance(event, ItemCommandEvent)
        print( f'{event}')

        # interaction is available through self.openhab or self.oh
        self.oh.post_update('TestItemUpdate', 123)

MyOpenhabRule()
```

# Changelog
#### 0.31.0 (08.10.2021)
- added self.get_items to easily search for items in a rule
- added full support for tags and groups on OpenhabItem
- Application should now properly shut down when there is a PermissionError
- Added DatetimeItem to docs
- Label in commandOption is optional
- Added message when file is removed
- Examples in the docs get checked with a newly created sphinx extension
- Reworked the openhab tests

#### 0.30.3 (17.06.2021)
- add support for custom ca cert for MQTT
- Scheduler runs only when the rule file has been loaded properly
- Sync openhab calls raise an error when called from an async context
- Replaced thread check for asyncio with a contextvar (internal)

#### 0.30.3 (01.06.2021)
- Scheduler runs only when the rule file has been loaded properly
- Replaced thread check for asyncio with a contextvar
- Sync openhab calls raise an error when called from an async context

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
  - Has now subsecond accuracity (finally!)
  - Has a new .coundown() job which can simplify many rules.
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
