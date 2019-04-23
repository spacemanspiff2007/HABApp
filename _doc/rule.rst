
.. module:: HABApp

Rule
==================================

.. |param_scheduled_time| replace:: Use a `datetime.time`_ object to specify a certain time of day,
   a `datetime.timedelta`_ object to specify a time in the future or None to use the current time.
.. |param_scheduled_cb| replace:: Function which will be called
.. |param_scheduled_cb_args| replace:: Positional arguments that will be passed to the function
.. |param_scheduled_cb_kwargs| replace:: Keyword arguments that will be passed to the function

.. _datetime.time: <https://docs.python.org/3/library/datetime.html#time-objects>
.. _datetime.timedelta: <https://docs.python.org/3/library/datetime.html#timedelta-objects>

Interacting with items
------------------------------
Items are like variables. They have a name and a state (which can be anything).
Items from openhab use the item name from openhab.
Items from MQTT use the topic as item name.

If an item value gets set there will be a :class:`~HABApp.core.ValueUpdateEvent` on the event bus.
If it changes there will be additionally a :class:`~HABApp.core.ValueChangeEvent`, too.


.. list-table::
   :widths: auto
   :header-rows: 1
   
   * - Function
     - Description
   
   * - :meth:`~HABApp.Rule.get_item_state`
     - Get the state of an item
     
   * - :meth:`~HABApp.Rule.set_item_state`
     - | Set the state of an item  to a new value (which can be anything).
       | This can also be used with custom class instances to load them from other rules.
         If the item doesn't exist yet it will be created.
       
   * - :meth:`~HABApp.Rule.item_exists`
     - Check if an item already exists.
     
   * - :meth:`~HABApp.Rule.item_watch`
     - | Keep watch on the state of an item.
       | If the item does not receive an update or change for a certain amount of time
         there will be a :class:`~HABApp.core.ValueNoUpdateEvent` or a :class:`~HABApp.core.ValueNoChangeEvent`
         on the event bus.

   * - :meth:`~HABApp.Rule.item_watch_and_listen`
     - Convenience function which combines :class:`~HABApp.Rule.item_watch` and :class:`~HABApp.Rule.listen_event`

Events
------------------------------

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Function
     - Description

   * - :meth:`~HABApp.Rule.listen_event`
     - Add a function which will be called as soon as an event occurs.
       The event will be passed as an argument into the function.
       There is the possibility to specify the event class which will reduce the function calls accordingly
       (typically :class:`~HABApp.core.ValueUpdateEvent` or :class:`~HABApp.core.ValueChangeEvent`).

Example::

    def __init__(self):
        super().__init__()
        self.listen_event('MyOpenhabItem', self.on_change, ValueChangeEvent)
        self.listen_event('My/MQTT/Topic', self.on_update, ValueUpdateEvent)

    def on_change(event):
        assert isinstance(event, ValueChangeEvent), type(event)

    def on_update(event):
        assert isinstance(event, ValueUpdateEvent), type(event)

Scheduler
------------------------------
With the scheduler it is easy to call functions in the future or periodically.
Do not use `time.sleep` but rather `self.run_in`.

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Function
     - Description

   * - :meth:`~HABApp.Rule.run_soon`
     - Run the callback as soon as possible (typically in the next second).

   * - :meth:`~HABApp.Rule.run_in`
     - Run the callback in x seconds.

   * - :meth:`~HABApp.Rule.run_at`
     - Run a function at a specified date_time

   * - :meth:`~HABApp.Rule.run_every`
     - Run a function periodically

   * - :meth:`~HABApp.Rule.run_minutely`
     - Run a function every minute

   * - :meth:`~HABApp.Rule.run_hourly`
     - Run a function every hour

   * - :meth:`~HABApp.Rule.run_daily`
     - Run a function every day

   * - :meth:`~HABApp.Rule.run_on_every_day`
     - Run a function at a specific time every day

   * - :meth:`~HABApp.Rule.run_on_workdays`
     - Run a function at a specific time on workdays

   * - :meth:`~HABApp.Rule.run_on_weekends`
     - Run a function at a specific time on weekends

   * - :meth:`~HABApp.Rule.run_on_day_of_week`
     - Run a function at a specific time on specific days of the week


All available functions
------------------------------
.. autoclass:: Rule
   :members:

   :var async_http: :ref:`Async http connections <ref_async_io>`
   :var mqtt: :ref:`MQTT interaction <ref_mqtt>`
   :var openhab: :ref:`Openhab interaction <ref_openhab>`
   :var oh: short alias for :py:class:`openhab` openhab
  

