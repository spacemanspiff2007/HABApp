
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
Items are like variables. They have a name and a value (which can be anything).
Items from openhab use the item name from openhab and get created when HABApp successfully connects to
openhab or when the openhab configuration changes.
Items from MQTT use the topic as item name and get created as soon as a message gets processed.

Some item types provide convenience functions, so it is advised to always set the correct item type.

The preferred way to get and create items is through the class factories :class:`~HABApp.core.items.Item.get_item`
and :class:`~HABApp.core.items.Item.get_create_item` since this ensures the proper item class and provides type hints when
using an IDE!

.. execute_code::
    :header_code: Example:
    :hide_output:

    from HABApp.core.items import Item
    my_item = Item.get_create_item('MyItem', initial_value=5)   # This will create the item if it does not exist
    my_item = Item.get_item('MyItem')                           # This will raise an exception if the item is not found
    print(my_item)


If an item value gets set there will be a :class:`~HABApp.core.ValueUpdateEvent` on the event bus.
If it changes there will be additionally a :class:`~HABApp.core.ValueChangeEvent`, too.

It is possible to check the item value by comparing it

.. execute_code::
    :hide_output:

    # hide
    from HABApp.core.items import Item
    Item.get_create_item('MyItem', initial_value=5)
    # hide

    from HABApp.core.items import Item
    my_item = Item.get_item('MyItem')

    # this works
    if my_item == 5:
        pass    # do something

    # and is the same as this
    if my_item.value == 5:
        pass    # do something


.. inheritance-diagram:: HABApp.core.items.Item
   :parts: 1

.. autoclass:: HABApp.core.items.Item
   :members:
   :inherited-members:


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

        # If you already have an item you can use the more convenient method of the item
        # to listen to the item events
        my_item = Item.get_item('MyItem')
        my_item.listen_event(self.on_change, ValueUpdateEvent)

    def on_change(self, event):
        assert isinstance(event, ValueChangeEvent), type(event)

    def on_update(self, event):
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

   * - :meth:`~HABApp.Rule.run_on_sun`
     - Run a function in relation to the sun (e.g. Sunrise, Sunset)

All functions return an instance of ScheduledCallbackBase

.. autoclass:: HABApp.rule.scheduler.base.ScheduledCallbackBase
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
With the proper import and type hint this method provides syntax checks and auto complete.

Rule instances can be accessed by their name (typically the class name). In the ``HABApp.log`` you can see the name when the rule is loaded.
If you want to assign a custom name, you can change the rule name easily by assigning it to ``self.rule_name`` in ``__init__``.

.. important:: Always look up rule every time, never assign to a class member!
               The rule might get reloaded and then the class member will still point to the old unloaded instance.


*rule_a.py*::

    import HABApp

    class ClassA(HABApp.Rule):
        ...

        def function_a(self):
          ...

    ClassA()

*rule_b.py*::

    import HABApp
    import typing

    if typing.TYPE_CHECKING:            # This is only here to allow
        from .rule_a import ClassA     # type hints for the IDE

    class ClassB(HABApp.Rule):
        ...

        def function_b(self):

            r = self.get_rule('ClassA')  # type: ClassA
            # The comment "# type: ClassA" will signal the IDE that the value returned from the
            # function is an instance of ClassA and thus provide checks and auto complete.

            # this calls the function on the instance
            r.function_a()



All available functions
------------------------------
.. autoclass:: HABApp.Rule
   :members:

   :var async_http: :ref:`Async http connections <ref_async_io>`
   :var mqtt: :ref:`MQTT interaction <ref_mqtt>`
   :var openhab: :ref:`Openhab interaction <ref_openhab>`
   :var oh: short alias for :py:class:`openhab` openhab
