
openHAB
==================================

Interaction with a openHAB
------------------------------
All interaction with the openHAB is done through the :py:attr:`self.oh` or :py:attr:`self.openhab` object in the rule.

.. image:: /gifs/openhab.gif



Function parameters
------------------------------
.. py:function:: self.openhab.post_update(item_name: str, state)

   Post a value to an item

   :param item_name: Item name
   :param state: new state


.. py:function:: self.openhab.send_command(item_name: str, command)

   Send a command to command to an item

   :param item_name: Item name
   :param command: command


.. py:function:: self.openhab.create_item(item_type: str, item_name: str[, label="", category="", tags=[], groups=[]])

   Adds a new item to the openhab item registry

   :param item_type:	Item type
   :param item_name:	Item name
   :param label:		Item label
   :param tags:		Item tags
   :param groups:		Item groups


.. py:function:: self.openhab.remove_item(item_name: str)

   Removes an item from the openhab item registry

   :param item_name: name of the item


Example openHAB rule
------------------
.. literalinclude:: ../conf/rules/openhab_rule.py
