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



Openhab item types
------------------------------

Openhab items are mapped to special classes and provide convenience functions.

Example:

.. execute_code::

    # hide
    import HABApp
    from HABApp.openhab.items import ContactItem, SwitchItem
    ContactItem.get_create_item('MyContact', initial_value='OPEN')
    SwitchItem.get_create_item('MySwitch', initial_value='OFF')
    # hide

    my_contact = ContactItem.get_item('MyContact')
    if my_contact.is_open():
        print('Contact is open!')

    my_switch = SwitchItem.get_item('MySwitch')
    if my_switch.is_on():
        my_switch.off()

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Openhab type
     - HABApp class
   * - ``Contact``
     - :class:`~HABApp.openhab.items.ContactItem`
   * - ``Switch``
     - :class:`~HABApp.openhab.items.SwitchItem`
   * - ``Dimmer``
     - :class:`~HABApp.openhab.items.DimmerItem`
   * - ``Rollershutter``
     - :class:`~HABApp.openhab.items.RollershutterItem`
   * - ``Color``
     - :class:`~HABApp.openhab.items.ColorItem`

.. autoclass:: HABApp.openhab.items.ContactItem
   :members:
   :inherited-members:
   :member-order: groupwise


.. autoclass:: HABApp.openhab.items.SwitchItem
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: HABApp.openhab.items.DimmerItem
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: HABApp.openhab.items.RollershutterItem
   :members:
   :inherited-members:
   :member-order: groupwise

.. autoclass:: HABApp.openhab.items.ColorItem
   :members:
   :inherited-members:
   :member-order: groupwise




Example openHAB rule
---------------------
.. literalinclude:: ../conf/rules/openhab_rule.py
