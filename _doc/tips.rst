**************************************
Tips & Tricks
**************************************


yml files
======================================

Entry sharing
--------------------------------------

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
      4: 80         #                  and then overwrites parameter 4



openHAB
======================================

autoupdate
--------------------------------------

If external devices are capable of reporting their state (e.g. Z-Wave) it is always advised to use disable ``autoupdate`` for these items.
This prevents openhab from guessing the item state based on the command and forces it to use the actual reported value.
If in doubt if the device supports reporting their state watch the state after sending a command with ``autoupdate`` off.
If the state changes ``autoupdate`` can remain off.


In the ``*.items`` file ``autoupdate`` can be disabled by adding the following statement in the metadata field.

```
Number	MyItem    { channel = "zwave:my_zwave_link", autoupdate="false" }
```

It's also possible with textual thing configuration to add it as :ref:`_ref_textual_thing_config_metadata`.
