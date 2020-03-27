# HABApp
[![Build Status](https://travis-ci.org/spacemanspiff2007/HABApp.svg?branch=master)](https://travis-ci.org/spacemanspiff2007/HABApp)
[![Documentation Status](https://readthedocs.org/projects/habapp/badge/?version=latest)](https://habapp.readthedocs.io/en/latest/?badge=latest)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/HABApp/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/HABApp/)

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

        self.run_every(
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