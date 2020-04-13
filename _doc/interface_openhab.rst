.. _ref_openhab:

openHAB
==================================

Interaction with a openHAB
------------------------------
All interaction with the openHAB is done through the ``self.oh`` or ``self.openhab`` object in the rule.

.. image:: /gifs/openhab.gif



Function parameters
------------------------------
.. autoclass:: HABApp.openhab.oh_interface.OpenhabInterface
   :members:

.. autoclass:: HABApp.openhab.oh_interface.OpenhabItemDefinition


Openhab item types
------------------------------

Description and example
^^^^^^^^^^^^^^^^^^^^^^^^

Openhab items are mapped to special classes and provide convenience functions.

Example:

.. execute_code::

    # hide
    import HABApp
    from HABApp.openhab.items import ContactItem, SwitchItem
    HABApp.core.Items.set_item(ContactItem('MyContact', initial_value='OPEN'))
    HABApp.core.Items.set_item(SwitchItem('MySwitch', initial_value='OFF'))
    # hide

    my_contact = ContactItem.get_item('MyContact')
    if my_contact.is_open():
        print('Contact is open!')

    my_switch = SwitchItem.get_item('MySwitch')
    if my_switch.is_on():
        my_switch.off()


NumberItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.NumberItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.NumberItem
   :members:
   :inherited-members:
   :member-order: groupwise


ContactItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.ContactItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ContactItem
   :members:
   :inherited-members:
   :member-order: groupwise


SwitchItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.SwitchItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.SwitchItem
   :members:
   :inherited-members:
   :member-order: groupwise


DimmerItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.DimmerItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.DimmerItem
   :members:
   :inherited-members:
   :member-order: groupwise


RollershutterItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.RollershutterItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.RollershutterItem
   :members:
   :inherited-members:
   :member-order: groupwise


ColorItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.ColorItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ColorItem
   :members:
   :inherited-members:
   :member-order: groupwise


StringItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.StringItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.StringItem
   :members:
   :inherited-members:
   :member-order: groupwise


LocationItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.LocationItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.LocationItem
   :members:
   :inherited-members:
   :member-order: groupwise


PlayerItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.PlayerItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.PlayerItem
   :members:
   :inherited-members:
   :member-order: groupwise


GroupItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.GroupItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.GroupItem
   :members:
   :inherited-members:
   :member-order: groupwise


Thing
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.Thing
   :parts: 1

.. autoclass:: HABApp.openhab.items.Thing
   :members:
   :inherited-members:
   :member-order: groupwise


ImageItem
^^^^^^^^^^^^^^^^^^^^^^^^
.. inheritance-diagram:: HABApp.openhab.items.ImageItem
   :parts: 1

.. autoclass:: HABApp.openhab.items.ImageItem
   :members:
   :inherited-members:
   :member-order: groupwise


Textual thing configuration
------------------------------

Description
^^^^^^^^^^^^^^^^^^^^^^^^

HABApp offers a special mechanism to textually define thing configuration parameters for things
which have been added through the gui. This combines the best of both worlds:
auto discovery and easy and fast sharing of parameters across things.

Configuration is done in the ``ThingConfig.yml`` file in the ``config`` folder (see :doc:`configuration`).
Just create an entry with the thing UID and the configuration parameters together with the target value.
Parameters will be checked/set when HABApp connects to openhab or when the file gets changed.

.. WARNING::
   The value of the parameters will not be checked and will be written as specified. It is recommended to use HABmin or PaperUI to
   generate the initial configuration and use this mechanism to spread it to things of the same type.

File Structure
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    ThingUID:
        Parameter1:  Value1
        Parameter2:  Value2

Examples
^^^^^^^^^^^^^^^^^^^^^^^^

The following example will show how to set the Z-Wave Parameters 4, 5 and 7 for a ``Philio PST02A`` Z-Wave sensor.

.. code-block:: yaml

    # Philio PST02A
    zwave:device:controller:node5:
      4: 99     # Light Threshold
      5: 8      # Operation Mode
      7: 20     # Customer Function


If the values should be checked for multiple sensors `yml features anchors <https://en.wikipedia.org/wiki/YAML#Advanced_components>`_
with ``&`` which then can be referenced with ``*``. This allows to apply the defined parameters quickly to more sensors.

.. code-block:: yaml

    # Philio PST02A
    zwave:device:controller:node3:  &PST02A  # <-- this creates the anchor with the name PST02A
      4: 99     # Light Threshold
      5: 8      # Operation Mode
      7: 20     # Customer Function

    zwave:device:controller:node5: *PST02A  # <-- this references the anchor with the name PST02A
    zwave:device:controller:node6: *PST02A
    zwave:device:controller:node7:
      <<: *PST02A   # <-- this references the anchor in merge mode
      4: 80         #     and overwrites parameter 4

*Log output*

.. code-block:: text

    [HABApp.openhab.Config]     INFO | Checking zwave:device:controller:node3: PhilioPST02A (Node 03)
    [HABApp.openhab.Config]     INFO |  - 4 is already 99
    [HABApp.openhab.Config]     INFO |  - 5 is already 8
    [HABApp.openhab.Config]     INFO |  - 7 is already 20
    [HABApp.openhab.Config]     INFO | Checking zwave:device:controller:node5: PhilioPST02A (Node 05)
    [HABApp.openhab.Config]     INFO |  - 4 is already 99
    [HABApp.openhab.Config]     INFO |  - 5 is already 8
    [HABApp.openhab.Config]     INFO |  - 7 is already 20
    [HABApp.openhab.Config]     INFO | Checking zwave:device:controller:node6: PhilioPST02A (Node 06)
    [HABApp.openhab.Config]     INFO |  - 4 is already 99
    [HABApp.openhab.Config]     INFO |  - 5 is already 8
    [HABApp.openhab.Config]     INFO |  - 7 is already 20
    [HABApp.openhab.Config]     INFO | Checking zwave:device:controller:node7: PhilioPST02A (Node 07)
    [HABApp.openhab.Config]     INFO |  - 4 is already 80
    [HABApp.openhab.Config]     INFO |  - 5 is already 8
    [HABApp.openhab.Config]     INFO |  - 7 is already 20


Parameter overview
^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to quickly generate a parameter overview (with current values) simply by specifying an invalid parameter name.

.. code-block:: yaml

    zwave:device:controller:node3:
      asdf: asdf

*Log output*

.. code-block:: text

    [HABApp.openhab.Config]     INFO | Checking zwave:device:controller:node3: PhilioPST02A (Node 03)
    [HABApp.openhab.Config]    ERROR |  - Config value "asdf" does not exist!
    [HABApp.openhab.Config]    ERROR |    Available:
    [HABApp.openhab.Config]    ERROR |     - Group1: ['controller']
    [HABApp.openhab.Config]    ERROR |     - Group2: []
    [HABApp.openhab.Config]    ERROR |     - binding_cmdrepollperiod: 1500
    [HABApp.openhab.Config]    ERROR |     - binding_pollperiod: 86400
    [HABApp.openhab.Config]    ERROR |     - wakeup_interval: 86400
    [HABApp.openhab.Config]    ERROR |     -   2: -1
    [HABApp.openhab.Config]    ERROR |     -   3: 80
    [HABApp.openhab.Config]    ERROR |     -   4: 99
    [HABApp.openhab.Config]    ERROR |     -   5: 8
    [HABApp.openhab.Config]    ERROR |     -   6: 0
    [HABApp.openhab.Config]    ERROR |     -   7: 20
    [HABApp.openhab.Config]    ERROR |     -   8: 3
    [HABApp.openhab.Config]    ERROR |     -   9: 4
    [HABApp.openhab.Config]    ERROR |     -  10: 12
    [HABApp.openhab.Config]    ERROR |     -  11: 12
    [HABApp.openhab.Config]    ERROR |     -  12: 12
    [HABApp.openhab.Config]    ERROR |     -  13: 12
    [HABApp.openhab.Config]    ERROR |     -  20: 30
    [HABApp.openhab.Config]    ERROR |     -  21: 0
    [HABApp.openhab.Config]    ERROR |     -  22: 0

Example openHAB rule
---------------------
.. literalinclude:: ../conf/rules/openhab_rule.py
