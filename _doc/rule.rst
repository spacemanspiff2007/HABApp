
.. module:: HABApp

Rule
==================================

.. |param_scheduled_cb| replace:: Function which will be called
.. |param_scheduled_cb_args| replace:: Positional arguments that will be passed to the function
.. |param_scheduled_cb_kwargs| replace:: Keyword arguments that will be passed to the function
   
.. autoclass:: Rule
   :members:

   :var async_http: :ref:`Async http connections <ref_async_io>`
   :var mqtt: :ref:`MQTT interaction <ref_mqtt>`
   :var openhab: :ref:`Openhab interaction <ref_openhab>`
   :var oh: short alias for :py:class:`openhab` openhab
  
