.. _ref_openhab:

openHAB
==================================

Interaction with a openHAB
------------------------------
All interaction with the openHAB is done through the ``self.oh`` or ``self.openhab`` object in the rule.

.. image:: /gifs/openhab.gif



Function parameters
------------------------------

.. py:class:: openhab
   
   .. py:method:: post_update(item_name: str, state)
   
      Post a value to an item
   
      :param item_name: Item name
      :param state: new state
   
   
   .. py:method:: send_command(item_name: str, command)
   
      Send a command to command to an item
   
      :param item_name: Item name
      :param command: command
   
   
   .. py:method:: create_item(item_type: str, item_name: str[, label="", category="", tags=[], groups=[]])
   
      Adds a new item to the openhab item registry
   
      :param item_type: Item type
      :param item_name: Item name
      :param label:     Item label
      :param tags:      Item tags
      :param groups:    Item groups
   
   
   .. py:method:: remove_item(item_name: str)
   
      Removes an item from the openhab item registry
   
      :param item_name: name of the item


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
