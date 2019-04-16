
.. module:: HABApp

Rule
==================================

.. |param_sched_cb| replace:: Function which will be called
.. |param_sched_cb_args| replace:: Positional arguments that will be passed to the function
.. |param_sched_cb_kwargs| replace:: Keyword arguments that will be passed to the function
   
.. autoclass:: Rule
   :members:

   :ivar async_http: :ref:`Async http connections <ref_async_io>`
   :ivar mqtt: :ref:`MQTT interaction <ref_mqtt>`
   :ivar openhab: :ref:`Openhab interaction <ref_openhab>`
   :ivar oh: short alias for **openhab**
  
