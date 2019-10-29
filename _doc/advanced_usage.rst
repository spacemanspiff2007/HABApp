
Advanced Usage
==================================

HABApp Topics
------------------------------
There are several internal topics which can be used to react to HABApp changes from within rules.
An example would be dynamically reloading rules when a parameter file gets reloaded
(e.g. when :class:`~HABApp.parameters.Parameter` is used to create rules dynamically) or
an own notifier in case there are errors (e.g. Pushover).

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Topic
     - Description
     - Events

   * - HABApp.Rules
     - The corresponding events trigger a load/unload of the rule file specified in the event
     - :class:`~HABApp.core.events.habapp_events.RequestFileLoadEvent` and :class:`~HABApp.core.events.habapp_events.RequestFileUnloadEvent`

   * - HABApp.Parameters
     - The corresponding events trigger a load/unload of the parameter file specified in the event
     - :class:`~HABApp.core.events.habapp_events.RequestFileLoadEvent` and :class:`~HABApp.core.events.habapp_events.RequestFileUnloadEvent`

   * - HABApp.Errors
     - All errors in functions and rules of HABApp create an according event. Use this topic to create an own notifier
       in case of errors (e.g. Pushover).
     - :class:`~HABApp.core.events.file_events.HABAppError`



.. autoclass:: HABApp.core.events.habapp_events.RequestFileLoadEvent
   :members:

.. autoclass:: HABApp.core.events.habapp_events.RequestFileUnloadEvent
   :members:

.. autoclass:: HABApp.core.events.habapp_events.HABAppError
   :members:
