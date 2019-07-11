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

Openhab items are mapped to special classes and provide convenience functions

Examples::

    my_contact = self.get_item('MyContact')
    if my_contact.is_open():
        pass

    my_switch = self.get_item('MySwitch')
    if my_switch.is_on():
        my_switch.off()



.. autoclass:: HABApp.openhab.items.ContactItem
   :members:
   
.. autoclass:: HABApp.openhab.items.SwitchItem
   :members:

.. autoclass:: HABApp.openhab.items.DimmerItem
   :members:

.. autoclass:: HABApp.openhab.items.RollershutterItem
   :members:



Example openHAB rule
---------------------
.. literalinclude:: ../conf/rules/openhab_rule.py
