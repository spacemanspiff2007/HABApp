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
   

Example openHAB rule
---------------------
.. literalinclude:: ../conf/rules/openhab_rule.py
