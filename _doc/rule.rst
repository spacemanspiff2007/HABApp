
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
Items from openhab use the item name from openhab and get created when HABApp successfully connects to
openhab or when the openhab configuration changes.
Items from MQTT use the topic as item name and get created as soon as a message gets processed.

Some item types provide convenience functions, so it is advised to always set the correct item type.

The preferred way to interact with items is through the class factory `get_create_item` since this provides type hints::

    from HABApp.core.items import Item
    my_item = Item.get_create_item('MyItem')

If an item value gets set there will be a :class:`~HABApp.core.ValueUpdateEvent` on the event bus.
If it changes there will be additionally a :class:`~HABApp.core.ValueChangeEvent`, too.

.. list-table::
   :widths: auto
   :header-rows: 1
   
   * - Function
     - Description
   
   * - :meth:`~HABApp.Rule.get_item`
     - Return an item (or create it if it doesn't exist yet)
     
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

It is possible to check the item value by comparing it::

    my_item = self.get_item('MyItem')

    # this works
    if my_item == 5:
        # do sth

    # and is the same as
    if my_item.state == 5:
        # do sth

.. autoclass:: HABApp.core.items.Item
   :members:


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
Do not use `time.sleep` but rather :meth:`~HABApp.Rule.run_in`.

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

All functions return an instance of ScheduledCallback

.. autoclass:: HABApp.rule.scheduler.ScheduledCallback
   :members:


Running external tools
------------------------------
External tools can be run with the :meth:`~HABApp.Rule.execute_subprocess` function.
Once the process has finished the callback will be called with an :class:`~HABApp.rule.FinishedProcessInfo` instance as first argument.
Example::

    import HABApp

    class MyExecutionRule(HABApp.Rule):

        def __init__(self):
            super().__init__()

            self.execute_subprocess( self.func_when_finished, 'path_to_program', 'arg1', capture_output=True)

        def func_when_finished(self, process_info):
            assert isinstance(process_info, HABApp.rule.FinishedProcessInfo)
            print(process_info)

    MyExecutionRule()


.. autoclass:: HABApp.rule.FinishedProcessInfo

   :var int returncode: Return code of the process (0: IO, -1: Exception while starting process)
   :var str stdout: Standard output of the process or None
   :var str stderr: Error output of the process or None

How to properly use rules from other rule files
-------------------------------------------------
This example shows how to properly get a rule during runtime and execute one of its function.
With the proper import this method provides syntax checks and auto complete.

**Important:** always look up rule every time, never assign to a class member!
The rule might get reloaded and then the class member will still point to the old unloaded instance.

Example::

    if typing.TYPE_CHECKING:
        from .class_b import ClassB

    class ClassA(Rule):
        ...

        def function_a(self):
            # Important: always look up rule every time, never assign to a class member!
            r = self.get_rule('NameOfRuleB')  # type: ClassB
            r.function_b()



All available functions
------------------------------
.. autoclass:: HABApp.Rule
   :members:

   :var async_http: :ref:`Async http connections <ref_async_io>`
   :var mqtt: :ref:`MQTT interaction <ref_mqtt>`
   :var openhab: :ref:`Openhab interaction <ref_openhab>`
   :var oh: short alias for :py:class:`openhab` openhab
