.. _ref_openhab:

######################################
openHAB
######################################


**************************************
Additional configuration
**************************************

For optimal performance it is recommended to use Basic Auth.
It can be enabled through GUI or through textual configuration.

Textual configuration
======================================
The settings are in the ``runtime.cfg``.
Remove the ``#`` before the entry to activate it.

.. code-block:: text

   ################ REST API ###################
   org.openhab.restauth:allowBasicAuth=true


GUI
======================================
It can be enabled through the gui in ``settings`` -> ``API Security`` -> ``Allow Basic Authentication``.

.. image:: /images/openhab_api_config.png


OpenHAB user
======================================
In case an additional openHAB user or token is created for HABApp it has to have admin rights.


.. _OPENHAB_ITEM_TYPES:


**************************************
openHAB item types
**************************************

.. |oh_item_desc_name| replace:: Item name
.. |oh_item_desc_value| replace:: Current item value (or state in openHAB wording)
.. |oh_item_desc_last_value| replace:: Last item value (or state in openHAB wording) before the current value one
.. |oh_item_desc_label| replace:: Item label or ``None`` if not configured
.. |oh_item_desc_tags| replace:: Item tags
.. |oh_item_desc_group| replace:: The groups the item is in
.. |oh_item_desc_metadata| replace:: Item metadata


Description and example
======================================
Items that are created from openHAB inherit all from :class:`~HABApp.openHAB.items.OpenhabItem` and
provide convenience functions which simplify many things.

Example:

.. exec_code::

    # ------------ hide: start ------------
    async def run(provider):
        from HABApp.testing import TestingItemFactory
        factory = await provider.get(TestingItemFactory)
        await factory.create('ContactItem', 'MyContact', value='OPEN')
        await factory.create('SwitchItem', 'MySwitch', value='OFF')
        # ------------ hide: stop -------------
        from HABApp.openhab.items import ContactItem, SwitchItem

        my_contact = ContactItem.get_item('MyContact')
        if my_contact.is_open():
            print('Contact is open!')

        my_switch = SwitchItem.get_item('MySwitch')
        if my_switch.is_on():
            my_switch.off()

    # ------------ hide: start ------------
    import doc_runner
    doc_runner.run(run)

NumberItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.NumberItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.NumberItem
   :members:
   :inherited-members:
   :member-order: groupwise


ContactItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.ContactItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ContactItem
   :members:
   :inherited-members:
   :member-order: groupwise


SwitchItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.SwitchItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.SwitchItem
   :members:
   :inherited-members:
   :member-order: groupwise


DimmerItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.DimmerItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.DimmerItem
   :members:
   :inherited-members:
   :member-order: groupwise


DatetimeItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.DatetimeItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.DatetimeItem
   :members:
   :inherited-members:
   :member-order: groupwise


RollershutterItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.RollershutterItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.RollershutterItem
   :members:
   :inherited-members:
   :member-order: groupwise


ColorItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.ColorItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ColorItem
   :members:
   :inherited-members:
   :member-order: groupwise


StringItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.StringItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.StringItem
   :members:
   :inherited-members:
   :member-order: groupwise


LocationItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.LocationItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.LocationItem
   :members:
   :inherited-members:
   :member-order: groupwise


PlayerItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.PlayerItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.PlayerItem
   :members:
   :inherited-members:
   :member-order: groupwise


GroupItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.GroupItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.GroupItem
   :members:
   :inherited-members:
   :member-order: groupwise


ImageItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.ImageItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ImageItem
   :members:
   :inherited-members:
   :member-order: groupwise


CallItem
======================================
.. inheritance-diagram:: HABApp.openhab.items.CallItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.CallItem
   :members:
   :inherited-members:
   :member-order: groupwise


Thing
======================================
.. inheritance-diagram:: HABApp.openhab.items.Thing
   :parts: 1

.. autoclass:: HABApp.openhab.items.Thing
   :members:
   :inherited-members:
   :member-order: groupwise



**************************************
Interaction with a openHAB
**************************************
All interaction with the openHAB is done through the ``self.oh`` or ``self.openhab`` object in the rule
or through an ``OpenhabItem``.

.. image:: /gifs/openhab.gif



Interface
======================================
.. autoclass:: HABApp.openhab.connection.handler.OpenHabSyncInterface
   :members:
   :inherited-members:


.. _OPENHAB_EVENT_TYPES:

**************************************
openHAB event types
**************************************

openHAB produces various events that are mapped to the internal event bus.
On the `openHAB page <https://next.openhab.org/docs/developer/utils/events.html#the-core-events>`_
there is an explanation for the various events.

Item events
======================================

ItemStateEvent
--------------------------------------
Since this event inherits from :class:`~HABApp.core.events.ValueUpdateEvent` you can listen to :class:`~HABApp.core.events.ValueUpdateEvent`
and it will also trigger for :class:`~HABApp.openhab.events.ItemStateEvent`.

.. inheritance-diagram:: HABApp.openhab.events.ItemStateEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemStateEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ItemStateChangedEvent
--------------------------------------
Since this event inherits from :class:`~HABApp.core.events.ValueChangeEvent` you can listen to :class:`~HABApp.core.events.ValueChangeEvent`
and it will also trigger for :class:`~HABApp.openhab.events.ItemStateChangedEvent`.

.. inheritance-diagram:: HABApp.openhab.events.ItemStateChangedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemStateChangedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ItemCommandEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemCommandEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemCommandEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ItemAddedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemAddedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemAddedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ItemUpdatedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemUpdatedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemUpdatedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ItemRemovedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemRemovedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemRemovedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ItemStatePredictedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemStatePredictedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemStatePredictedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


GroupStateChangedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.GroupStateChangedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.GroupStateChangedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


Channel events
======================================


ChannelTriggeredEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ChannelTriggeredEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ChannelTriggeredEvent
   :members:
   :inherited-members:
   :member-order: groupwise


Thing events
======================================


ThingAddedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ThingAddedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ThingAddedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ThingUpdatedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ThingUpdatedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ThingUpdatedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ThingRemovedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ThingRemovedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ThingRemovedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ThingStatusInfoEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ThingStatusInfoEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ThingStatusInfoEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ThingStatusInfoChangedEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ThingStatusInfoChangedEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ThingStatusInfoChangedEvent
   :members:
   :inherited-members:
   :member-order: groupwise


ThingFirmwareStatusInfoEvent
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ThingFirmwareStatusInfoEvent
   :parts: 1

.. autoclass:: HABApp.openhab.events.ThingFirmwareStatusInfoEvent
   :members:
   :inherited-members:
   :member-order: groupwise


Event filters
======================================


ItemStateUpdatedEventFilter
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemStateUpdatedEventFilter
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemStateUpdatedEventFilter
   :members:
   :inherited-members:
   :member-order: groupwise


ItemStateChangedEventFilter
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemStateChangedEventFilter
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemStateChangedEventFilter
   :members:
   :inherited-members:
   :member-order: groupwise


ItemCommandEventFilter
--------------------------------------
.. inheritance-diagram:: HABApp.openhab.events.ItemCommandEventFilter
   :parts: 1

.. autoclass:: HABApp.openhab.events.ItemCommandEventFilter
   :members:
   :inherited-members:
   :member-order: groupwise

**************************************
Transformations
**************************************

From openHAB 4 on it's possible to use the existing transformations in HABApp.
Transformations are loaded every time when HABApp connects to openHAB.
OpenHAB does not issue an event when the transformations change so in order for HABApp to
pick up the changes either HABApp or openHAB has to be restarted.
Available transformations are logged on connect.

map
======================================
The `map transformation <https://www.openhab.org/addons/transformations/map/>`_ is returned as a dict.
If the map transformation is defined with a default the default is used accordingly.

Example:

.. exec_code::
    hide_output

    # ------------ hide: start ------------
    from HABApp.openhab.transformations._map.registry import MAP_REGISTRY
    MAP_REGISTRY.objs['test.map'] = {'test_key': 'test_value'}, None
    MAP_REGISTRY.objs['numbers.map'] = {1: 'test number meaning'}, None

    # ------------ hide: stop -------------
    from HABApp.openhab import transformations

    TEST_MAP = transformations.map['test.map']  # load the transformation, can be used anywhere
    print(TEST_MAP['test_key'])                 # It's a normal dict with keys as str and values as str

    # if all keys or values are numbers they are automatically casted to an int
    NUMBERS = transformations.map['numbers.map']
    print(NUMBERS[1])   # Note that the key is an int


**************************************
Example openHAB rules
**************************************

Example 1
======================================
.. literalinclude:: ../run/conf/rules/openhab_rule.py


Check status of things
======================================
This rule prints the status of all ``Things`` and shows how to subscribe to events of the ``Thing`` status

.. literalinclude:: ../run/conf/rules/openhab_things.py

Check status if thing is constant
======================================
Sometimes ``Things`` recover automatically from small outages. This rule only triggers when the ``Thing`` is constant
for 60 seconds.

.. exec_code::

    # ------------ hide: start ------------
    async def run(provider):

        from HABApp.testing import TestingItemFactory
        factory = await provider.get(TestingItemFactory)
        thing_item = await factory.create('Thing', 'my:thing:uid')
    # ------------ hide: stop -------------

        from HABApp import Rule
        from HABApp.core.events import ItemNoChangeEvent
        from HABApp.openhab.items import Thing


        class CheckThing(Rule):
            def __init__(self, name: str):
                super().__init__()

                self.thing = Thing.get_item(name)
                watcher = self.thing.watch_change(60)
                watcher.listen_event(self.thing_no_change)

            def thing_no_change(self, event: ItemNoChangeEvent):
                print(f'Thing {event.name} constant for {event.seconds}')
                print(f'Status: {self.thing.status}')


        CheckThing('my:thing:uid')

    # ------------ hide: start ------------
        thing_item.status = 'ONLINE'
        from HABApp.core.internals import EventBus
        provider.get_existing(EventBus).post_event('my:thing:uid', ItemNoChangeEvent('test_watch', 60))

    import doc_runner
    doc_runner.run(run)
