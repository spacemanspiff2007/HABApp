.. _ref_async_io:

asyncio
==================================

.. WARNING::
   | Please make sure you know what you are doing when using async functions!
   | If you have no asyncio experience please do not use this!
     The use of blocking calls in async functions will prevent HABApp from working properly!



async http
""""""""""""""""""""""""""""""
Async http calls are available through the ``self.async_http`` object in rule instances.

Functions
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: HABApp.rule.interfaces.http
   :members:
   :imported-members:

Examples
^^^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../run/conf/rules/async_rule.py
