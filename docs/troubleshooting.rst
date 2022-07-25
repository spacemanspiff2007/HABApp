**************************************
Troubleshooting
**************************************


Errors
======================================

ValueError: Line is too long
--------------------------------------

The underlaying libraries of HABApp use a buffer to process each request and event from openHAB.
If the openHAB items contain images this buffer might be not enough and a ``ValueError: Line is too long``
error will appear in the logs. See :ref:`the openHAB connection options<CONFIG_OPENHAB_CONNECTION>` on how to increase
the buffer. The maximum image size that can be used without error is ~40% of the buffer size.
