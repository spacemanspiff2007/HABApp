.. _ref_openhab:

openHAB
==================================

Interaction with a openHAB
------------------------------
All interaction with the openHAB is done through the ``self.oh`` or ``self.openhab`` object in the rule.

.. image:: /gifs/openhab.gif



Function parameters
------------------------------
.. automodule:: HABApp.openhab.interface
   :members:
   :imported-members:


.. _OPENHAB_ITEM_TYPES:

Openhab item types
------------------------------

Description and example
~~~~~~~~~~~~~~~~~~~~~~~~

Openhab items are mapped to special classes and provide convenience functions.

Example:

.. execute_code::

    # hide
    import HABApp
    from HABApp.openhab.items import ContactItem, SwitchItem
    HABApp.core.Items.add_item(ContactItem('MyContact', initial_value='OPEN'))
    HABApp.core.Items.add_item(SwitchItem('MySwitch', initial_value='OFF'))
    # hide
    from HABApp.openhab.items import ContactItem, SwitchItem

    my_contact = ContactItem.get_item('MyContact')
    if my_contact.is_open():
        print('Contact is open!')

    my_switch = SwitchItem.get_item('MySwitch')
    if my_switch.is_on():
        my_switch.off()


NumberItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.NumberItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.NumberItem
   :members:
   :inherited-members:
   :member-order: groupwise


ContactItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.ContactItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ContactItem
   :members:
   :inherited-members:
   :member-order: groupwise


SwitchItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.SwitchItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.SwitchItem
   :members:
   :inherited-members:
   :member-order: groupwise


DimmerItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.DimmerItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.DimmerItem
   :members:
   :inherited-members:
   :member-order: groupwise


RollershutterItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.RollershutterItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.RollershutterItem
   :members:
   :inherited-members:
   :member-order: groupwise


ColorItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.ColorItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ColorItem
   :members:
   :inherited-members:
   :member-order: groupwise


StringItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.StringItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.StringItem
   :members:
   :inherited-members:
   :member-order: groupwise


LocationItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.LocationItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.LocationItem
   :members:
   :inherited-members:
   :member-order: groupwise


PlayerItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.PlayerItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.PlayerItem
   :members:
   :inherited-members:
   :member-order: groupwise


GroupItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.GroupItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.GroupItem
   :members:
   :inherited-members:
   :member-order: groupwise


ImageItem
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.ImageItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ImageItem
   :members:
   :inherited-members:
   :member-order: groupwise


Thing
~~~~~~~~~~~~~~~~~~~~~~~~
.. inheritance-diagram:: HABApp.openhab.items.Thing
   :parts: 1

.. autoclass:: HABApp.openhab.items.Thing
   :members:
   :inherited-members:
   :member-order: groupwise


Textual thing configuration
------------------------------

Description
~~~~~~~~~~~~~~~~~~~~~~~~

HABApp offers a special mechanism to textually define thing configuration parameters and linked items for things
which have been added through the gui.
This combines the best of both worlds:
auto discovery, easy and fast sharing of parameters and items across things.

.. WARNING::
   The value of the configuration parameters will not be checked and will be written as specified.
   It is recommended to use HABmin or PaperUI to generate the initial configuration and use this mechanism to spread
   it to things of the same type.

Configuration is done in the ``thing_your_name.yml`` file in the ``config`` folder (see :doc:`configuration`).
Every file that starts with ``thing_`` has the ``.yml`` ending will be loaded.

The Parameters and items will be checked/set when HABApp connects to openHAB or
whenever the corresponding file gets changed.

Principle of operation
~~~~~~~~~~~~~~~~~~~~~~~~
All existing things from openHAB can be filtered by different criteria.
For each one of these things it is then possible to

* Set thing parameters
* Create items with wildcards taken from the thing
* | Apply filters to the channels of the thing.
  | For each matching channel it is possible to link items with wildcards taken from the thing and the matching channel

There is also a test mode which prints out all required information and does not make any changes.

A valid ``.items`` file will automatically be created next to the ``.yml`` file containing all created items.
It can be used to get a quick overview what items (would) have been created or copied into the items folder.

File Structure
~~~~~~~~~~~~~~~~~~~~
Configuration is done through a .yml file.

Example
"""""""""""""""""""""""""""""

The following example will show how to set the Z-Wave Parameters 4, 5, 6 and 8 for a ``Philio PST02A`` Z-Wave sensor
and how to automatically link items to it.

.. tip::
   Integer values can be specified either as integer (``20``) or hex (``0x14``)

The entries ``thing config``, ``create items`` and ``channels`` are optional and can be combined as desired.

.. code-block:: yaml

   # Test mode: will not do anything but instead print out information
   test: True

   # Define filters which will reduce the number of things,
   # all defined filters have to match for further processing
   filter:
     thing_type: zwave:philio_pst02a_00_000

   # Set this configuration every matching thing. HABApp will automatically only 
   # change the values which are not already correct.
   # Here it is the z-wave parameters which are responsible for the device behaviour
   thing config:
     4: 99     # Light Threshold
     5: 8      # Operation Mode
     6: 4      # MultiSensor Function Switch
     7: 20     # Customer Function

   # Create items for every matching thing
   create items:
    - type: Number
      name: '{thing_label, :(.+)$}_MyNumber'          # Use the label from the thing as an input for the name,
      label: '{thing_label, :(.+)$} MyNumber [%d]'    # the regex will take everything from the ':' on until the end
      icon: battery

   channels:
     # reduce the channels of the thing with these filters
     # and link items to it
     - filter:
         channel_type: zwave:alarm_motion
       link items:
         - type: Number
           name: '{thing_label, :(.+)$}_Movement'           # Use the label from the thing as an input for the name,
           label: '{thing_label, :(.+)$} Movement [%d %%]'  # the regex will take everything from the ':' on until the end
           icon: battery
           groups: ['group1', 'group2']
           tags: ['tag1']

     - filter:
         channel_type: zwave:sensor_temperature
       link items:
         - type: Number
           name: '{thing_label, :(.+)$}_Temperature'
           label: '{thing_label, :(.+)$} Temperature [%d %%]'
           icon: battery


Multiple thing definitions in one file
""""""""""""""""""""""""""""""""""""""""

It is possible to add multiple thing processors into one file.
To achieve this the root entry is now a list.

Filters can also be lists e.g. if the have to be applied multiple times to the same filed.

.. code-block:: yaml
   :emphasize-lines: 1,6,9,10

   - test: True
     filter:
       thing_type: zwave:philio_pst02a_00_000
     ...

   - test: True
     # multiple filters on the same field, all have to match
     filter:
     - thing_type: zwave:fibaro.+
     - thing_type: zwave:fibaro_fgrgbw_00_000
     ...


Adding Metadata to items
"""""""""""""""""""""""""""""
It is possible to add metadata to the created items through the optional ``metadata`` entry in the item config.

There are two forms how metadata can be set. The implicit form for simple key-value pairs (e.g. ``autoupdate``) or
the explicit form where the entries are unter ``value`` and ``config`` (e.g. ``alexa``)

.. code-block:: yaml
   :emphasize-lines: 5,6,8,9,10,11,12

   - type: Number
     name: '{thing_label, :(.+)$}_Temperature'
     label: '{thing_label, :(.+)$} Temperature [%d %%]'
     icon: battery
     metadata:
       autoupdate: 'false'
       homekit: 'TemperatureSensor'
       alexa:
         'value': 'Fan'
         'config':
           'type': 'oscillating'
           'speedSteps': 3

The config is equivalent to the following item configuration::

   Number MyLabel_Temperature  "MyLabel Temperature [%d %%]" { autoupdate="false", homekit="TemperatureSensor", alexa="Fan" [ type="oscillating", speedSteps=3 ] }




References in thing config
~~~~~~~~~~~~~~~~~~~~~~~~~~
It is possible to use references to mathematically build parameters from other parameters.
Typically this would be fade duration and refresh interval.
References to other parameter values can be created with ``$``.
Example:

.. code-block:: yaml

   thing config:
     5: 8
     6: '$5 / 2'       # Use value from parameter 5 and divide it by two.
     7: 'int($5 / 2)'  # it is possible to use normal python datatypes


Wildcards for items and channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Wildcards are available for item configuration and can be applied to all fields except for 'type' and 'metadata'.

Syntax
"""""""""""""
Wildcards are framed with ``{}`` so the containing string has to be put in annotation marks.
There are three modes of operation with wildcards:

1. | Just insert the value from the wildcard:
   | ``{wildcard}``
2. | Insert a part of the value from the wildcard. A regular expression is used to extract the part and
     therefore has to contain a capturing group.
   | ``{wildcard, regex(with_group)}``
3. | Do a regex, replace on the value from the wildcard and use the result
   | ``{wildcard, regex, replace}``

Available wildcards
"""""""""""""""""""""
The following wildcards are available for things:

* ``thing_uid``
* ``thing_type``
* ``thing_location``
* ``thing_label``
* ``bridge_uid``

Additional available wildcards for channels:

* ``channel_uid``
* ``channel_type``
* ``channel_label``
* ``channel_kind``

.. tip::
   Test mode will show a table with all available wildcards and their value


Example
~~~~~~~~~~

Log output
"""""""""""""""""""""
This will show the output for the example from `File Structure`_

.. code-block:: text

   Loading /config/thing_philio.yml!
   +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
   |                                                                                   Thing overview                                                                                 |
   +---------------------------------+----------------------------+----------------+----------------------------------------+----------------------------------------------+----------+
   |           thing_uid             |         thing_type         | thing_location |            thing_label                 |                  bridge_uid                  | editable |
   +---------------------------------+----------------------------+----------------+----------------------------------------+----------------------------------------------+----------+
   | zwave:device:controller:node32  | zwave:fibaro_fgrgbw_00_000 | Room1          | Fibaro RGBW (Node 32): Room1 RGBW      | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node7   | zwave:fibaro_fgrgbw_00_000 | Room2          | Fibaro RGBW (Node 07): Room2 RGBW      | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node23  | zwave:fibaro_fgrgbw_00_000 | Room3          | Fibaro RGBW (Node 23): Room3 RGBW      | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node35  | zwave:philio_pst02a_00_000 | Room1          | Philio PST02A (Node 35): Room1 Door    | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node15  | zwave:philio_pst02a_00_000 | Room2          | Philio PST02A (Node 15): Room2 Window  | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node17  | zwave:philio_pst02a_00_000 | Room3          | Philio PST02A (Node 17): Room3 Window  | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node3   | zwave:philio_pst02a_00_000 | Room1          | Philio PST02A (Node 03): Room1 Window  | zwave:serial_zstick:controller               | True     |
   | zwave:device:controller:node5   | zwave:philio_pst02a_00_000 | Room4          | Philio PST02A (Node 05): FrontDoor     | zwave:serial_zstick:controller               | True     |
   | zwave:serial_zstick:controller  | zwave:serial_zstick        |                | ZWave Controller                       |                                              | False    |
   +---------------------------------+----------------------------+----------------+----------------------------------------+----------------------------------------------+----------+
   thing_type "zwave:philio_pst02a_00_000" matches for zwave:device:controller:node35!
   thing_type "zwave:philio_pst02a_00_000" matches for zwave:device:controller:node15!
   thing_type "zwave:philio_pst02a_00_000" matches for zwave:device:controller:node17!
   thing_type "zwave:philio_pst02a_00_000" matches for zwave:device:controller:node3!
   thing_type "zwave:philio_pst02a_00_000" matches for zwave:device:controller:node5!
   +---------------------------------------------------------------------------------------------------------------------------+
   |                                                   Current configuration                                                   |
   +-------------------------+-------------------+-------------------+-------------------+------------------+------------------+
   |        Parameter        | controller:node35 | controller:node15 | controller:node17 | controller:node3 | controller:node5 |
   +-------------------------+-------------------+-------------------+-------------------+------------------+------------------+
   | 2                       | -1                | -1                | -1                | -1               | -1               |
   | 3                       | 80                | 80                | 80                | 80               | 80               |
   | 4                       | 99                | 99                | 99                | 99               | 99               |
   | 5                       | 0                 | 8                 | 8                 | 8                | 8                |
   | 6                       | 4                 | 0                 | 0                 | 0                | 0                |
   | 7                       | 22                | 20                | 20                | 20               | 20               |
   | 8                       | 3                 | 3                 | 3                 | 3                | 3                |
   | 9                       | 4                 | 0                 | 4                 | 4                | 4                |
   | 10                      | 12                | 12                | 12                | 12               | 12               |
   | 11                      | 12                | 12                | 12                | 12               | 12               |
   | 12                      | 12                | 12                | 2                 | 12               | 4                |
   | 13                      | 12                | 12                | 2                 | 12               | 4                |
   | 20                      | 30                | 30                | 30                | 30               | 30               |
   | 21                      | 1                 | 0                 | 0                 | 0                | 0                |
   | 22                      | 0                 | 0                 | 0                 | 0                | 0                |
   | Group1                  | ['controller']    | ['controller']    | ['controller']    | ['controller']   | ['controller']   |
   | Group2                  | []                | []                | []                | []               | []               |
   | binding_cmdrepollperiod | 1500              | 1500              | 1500              | 1500             | 1500             |
   | binding_pollperiod      | 86400             | 86400             | 86400             | 86400            | 86400            |
   | wakeup_interval         | 86400             | 86400             | 86400             | 86400            | 86400            |
   +-------------------------+-------------------+-------------------+-------------------+------------------+------------------+
   Would set {5: 8, 7: 20} for zwave:device:controller:node35
   Would set {6: 4} for zwave:device:controller:node15
   Would set {6: 4} for zwave:device:controller:node17
   Would set {6: 4} for zwave:device:controller:node3
   Would set {6: 4} for zwave:device:controller:node5
   +----------------------------------------------------------------------------------------------------------------------+
   |                                       Channels for zwave:philio_pst02a_00_000                                        |
   +---------------------------------------------------+--------------------------+------------------------+--------------+
   |                    channel_uid                    |       channel_type       |     channel_label      | channel_kind |
   +---------------------------------------------------+--------------------------+------------------------+--------------+
   | zwave:device:controller:node35:sensor_door        | zwave:sensor_door        | Door/Window Sensor     | STATE        |
   | zwave:device:controller:node35:alarm_motion       | zwave:alarm_motion       | Motion Sensor          | STATE        |
   | zwave:device:controller:node35:alarm_tamper       | zwave:alarm_tamper       | Tamper Alarm           | STATE        |
   | zwave:device:controller:node35:sensor_luminance   | zwave:sensor_luminance   | Sensor (luminance)     | STATE        |
   | zwave:device:controller:node35:sensor_temperature | zwave:sensor_temperature | Sensor (temperature)   | STATE        |
   | zwave:device:controller:node35:alarm_access       | zwave:alarm_access       | Alarm (Access Control) | STATE        |
   | zwave:device:controller:node35:alarm_burglar      | zwave:alarm_burglar      | Alarm (Burglar)        | STATE        |
   | zwave:device:controller:node35:battery-level      | system:battery-level     | Batterieladung         | STATE        |
   +---------------------------------------------------+--------------------------+------------------------+--------------+
   channel_type "zwave:alarm_motion" matches for zwave:device:controller:node35:alarm_motion!
   channel_type "zwave:sensor_temperature" matches for zwave:device:controller:node35:sensor_temperature!

   channel_type "zwave:alarm_motion" matches for zwave:device:controller:node15:alarm_motion!
   channel_type "zwave:sensor_temperature" matches for zwave:device:controller:node15:sensor_temperature!

   channel_type "zwave:alarm_motion" matches for zwave:device:controller:node17:alarm_motion!
   channel_type "zwave:sensor_temperature" matches for zwave:device:controller:node17:sensor_temperature!

   channel_type "zwave:alarm_motion" matches for zwave:device:controller:node3:alarm_motion!
   channel_type "zwave:sensor_temperature" matches for zwave:device:controller:node3:sensor_temperature!

   channel_type "zwave:alarm_motion" matches for zwave:device:controller:node5:alarm_motion!
   channel_type "zwave:sensor_temperature" matches for zwave:device:controller:node5:sensor_temperature!

   Would create Item(type='Number', name='Room1_Door_MyNumber', label='Room1 Door MyNumber [%d]', icon='battery', groups=[], tags=[], link=None)
   Would create Item(type='Number', name='Room1_Door_Movement', label='Room1 Door Movement [%d %%]', icon='battery', groups=['group1', 'group2'], tags=['tag1'], link='zwave:device:controller:node35:alarm_motion')
   Would create Item(type='Number', name='Room1_Door_Temperature', label='Room1 Door Temperature [%d %%]', icon='battery', groups=[], tags=[], link='zwave:device:controller:node35:sensor_temperature')
   Would create Item(type='Number', name='Room2_Window_MyNumber', label='Room2 Window MyNumber [%d]', icon='battery', groups=[], tags=[], link=None)
   Would create Item(type='Number', name='Room2_Window_Movement', label='Room2 Window Movement [%d %%]', icon='battery', groups=['group1', 'group2'], tags=['tag1'], link='zwave:device:controller:node15:alarm_motion')
   Would create Item(type='Number', name='Room2_Window_Temperature', label='Room2 Window Temperature [%d %%]', icon='battery', groups=[], tags=[], link='zwave:device:controller:node15:sensor_temperature')
   Would create Item(type='Number', name='Room3_Window_MyNumber', label='Room3 Window MyNumber [%d]', icon='battery', groups=[], tags=[], link=None)
   Would create Item(type='Number', name='Room3_Window_Movement', label='Room3 Window Movement [%d %%]', icon='battery', groups=['group1', 'group2'], tags=['tag1'], link='zwave:device:controller:node17:alarm_motion')
   Would create Item(type='Number', name='Room3_Window_Temperature', label='Room3 Window Temperature [%d %%]', icon='battery', groups=[], tags=[], link='zwave:device:controller:node17:sensor_temperature')
   Would create Item(type='Number', name='Room1_Window_MyNumber', label='Room1 Window MyNumber [%d]', icon='battery', groups=[], tags=[], link=None)
   Would create Item(type='Number', name='Room1_Window_Movement', label='Room1 Window Movement [%d %%]', icon='battery', groups=['group1', 'group2'], tags=['tag1'], link='zwave:device:controller:node3:alarm_motion')
   Would create Item(type='Number', name='Room1_Window_Temperature', label='Room1 Window Temperature [%d %%]', icon='battery', groups=[], tags=[], link='zwave:device:controller:node3:sensor_temperature')
   Would create Item(type='Number', name='FrontDoor_MyNumber', label='FrontDoor MyNumber [%d]', icon='battery', groups=[], tags=[], link=None)
   Would create Item(type='Number', name='FrontDoor_Movement', label='FrontDoor Movement [%d %%]', icon='battery', groups=['group1', 'group2'], tags=['tag1'], link='zwave:device:controller:node5:alarm_motion')
   Would create Item(type='Number', name='FrontDoor_Temperature', label='FrontDoor Temperature [%d %%]', icon='battery', groups=[], tags=[], link='zwave:device:controller:node5:sensor_temperature')



Created items file
"""""""""""""""""""""

.. code-block:: text

   Number   Room1_Door_MyNumber         "Room1 Door MyNumber [%d]"             <battery>
   Number   Room1_Door_Movement         "Room1 Door Movement [%d %%]"          <battery>    (group1, group2)     [tag1]   {channel = "zwave:device:controller:node35:alarm_motion"}
   Number   Room1_Door_Temperature      "Room1 Door Temperature [%d %%]"       <battery>                                  {channel = "zwave:device:controller:node35:sensor_temperature"}
   Number   Room2_Window_MyNumber       "Room2 Window MyNumber [%d]"           <battery>
   Number   Room2_Window_Movement       "Room2 Window Movement [%d %%]"        <battery>    (group1, group2)     [tag1]   {channel = "zwave:device:controller:node15:alarm_motion"}
   Number   Room2_Window_Temperature    "Room2 Window Temperature [%d %%]"     <battery>                                  {channel = "zwave:device:controller:node15:sensor_temperature"}
   Number   Room3_Window_MyNumber       "Room3 Window MyNumber [%d]"           <battery>
   Number   Room3_Window_Movement       "Room3 Window Movement [%d %%]"        <battery>    (group1, group2)     [tag1]   {channel = "zwave:device:controller:node17:alarm_motion"}
   Number   Room3_Window_Temperature    "Room3 Window Temperature [%d %%]"     <battery>                                  {channel = "zwave:device:controller:node17:sensor_temperature"}
   Number   Room1_Window_MyNumber       "Room1 Window MyNumber [%d]"           <battery>
   Number   Room1_Window_Movement       "Room1 Window Movement [%d %%]"        <battery>    (group1, group2)     [tag1]   {channel = "zwave:device:controller:node3:alarm_motion"}
   Number   Room1_Window_Temperature    "Room1 Window Temperature [%d %%]"     <battery>                                  {channel = "zwave:device:controller:node3:sensor_temperature"}
   Number   FrontDoor_MyNumber          "FrontDoor MyNumber [%d]"              <battery>
   Number   FrontDoor_Movement          "FrontDoor Movement [%d %%]"           <battery>    (group1, group2)     [tag1]   {channel = "zwave:device:controller:node5:alarm_motion"}
   Number   FrontDoor_Temperature       "FrontDoor Temperature [%d %%]"        <battery>                                  {channel = "zwave:device:controller:node5:sensor_temperature"}


Entry sharing
""""""""""""""""

If the values should be reused `yml features anchors <https://en.wikipedia.org/wiki/YAML#Advanced_components>`_
with ``&`` which then can be referenced with ``*``. This allows to reuse the defined structures:

.. code-block:: yaml

    my_key_value_pairs:  &my_kv  # <-- this creates the anchor node with the name my_kv
      4: 99     # Light Threshold
      5: 8      # Operation Mode
      7: 20     # Customer Function

    value_1: *my_kv  # <-- '*my_kv' references the anchor node my_kv
    value_2: *my_kv
    value_3:
      <<: *my_kv    # <-- '<<: *my_kv' references and inserts the content (!) of the anchor node my_kv
      4: 80         #     and then overwrites parameter 4




Example openHAB rules
---------------------

Example 1
~~~~~~~~~~~~~~~~~~~~~~~~
.. literalinclude:: ../conf/rules/openhab_rule.py


Check status of things
~~~~~~~~~~~~~~~~~~~~~~~~
This rule prints the status of all ``Things`` and shows how to subscribe to events of the ``Thing`` status

.. literalinclude:: ../conf/rules/openhab_things.py

Check status if thing is constant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sometimes ``Things`` recover automatically from small outages. This rule only triggers then the ``Thing`` is constant
for 60 seconds.

.. execute_code::

    # hide
    import time, HABApp
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    thing_item = HABApp.openhab.items.Thing('my:thing:uid')
    HABApp.core.Items.add_item(thing_item)
    # hide
    from HABApp import Rule
    from HABApp.core.events import ItemNoChangeEvent
    from HABApp.openhab.items import Thing


    class CheckThing(Rule):
        def __init__(self, name: str):
            super().__init__()

            self.thing = Thing.get_item(name)
            watcher = self.thing.watch_change(60)
            self.thing.listen_event(self.thing_no_change, watcher.EVENT)

        def thing_no_change(self, event: ItemNoChangeEvent):
            print(f'Thing {event.name} constant for {event.seconds}')
            print(f'Status: {self.thing.status}')


    CheckThing('my:thing:uid')
    # hide
    thing_item.status = 'ONLINE'
    HABApp.core.EventBus.post_event('my:thing:uid', ItemNoChangeEvent('test_watch', 60))
    runner.tear_down()
    # hide

