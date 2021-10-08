
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

.. exec_code::
    :caption: Example:
    :hide_output:

    from HABApp.core.items import Item
    my_item = Item.get_create_item('MyItem', initial_value=5)   # This will create the item if it does not exist
    my_item = Item.get_item('MyItem')                           # This will raise an exception if the item is not found
    print(my_item)


If an item value gets set there will be a :class:`~HABApp.core.ValueUpdateEvent` on the event bus.
If it changes there will be additionally a :class:`~HABApp.core.ValueChangeEvent`, too.

It is possible to check the item value by comparing it

.. exec_code::
    :hide_output:

    # ------------ hide: start ------------
    from HABApp.core.items import Item
    Item.get_create_item('MyItem', initial_value=5)
    # ------------ hide: stop -------------

    from HABApp.core.items import Item
    my_item = Item.get_item('MyItem')

    # this works
    if my_item == 5:
        pass    # do something

    # and is the same as this
    if my_item.value == 5:
        pass    # do something

An overview over the item types can be found on :ref:`the HABApp item section <HABAPP_ITEM_TYPES>`,
:ref:`the openhab item section <OPENHAB_ITEM_TYPES>` and the :ref:`the mqtt item section <MQTT_ITEM_TYPES>`

Events
------------------------------

It is possible to listen to events through the :meth:`~HABApp.Rule.listen_event` function.
The passed function will be called as soon as an event occurs and the event will pe passed as an argument
into the function.

There is the possibility to reduce the function calls to a certain event type with an additional parameter
(typically :class:`~HABApp.core.ValueUpdateEvent` or :class:`~HABApp.core.ValueChangeEvent`).

An overview over the events can be found on :ref:`the HABApp event section <HABAPP_EVENT_TYPES>`,
:ref:`the openhab event section <OPENHAB_EVENT_TYPES>` and the :ref:`the mqtt event section <MQTT_EVENT_TYPES>`

.. exec_code::
    :hide_output:
    :caption: Example

    # ------------ hide: start ------------
    import time, HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.create_item('MyItem', HABApp.core.items.Item)
    # ------------ hide: stop -------------
    from HABApp import Rule
    from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
    from HABApp.core.items import Item

    class MyRule(Rule):
        def __init__(self):
            super().__init__()
            self.listen_event('MyOpenhabItem', self.on_change, ValueChangeEvent)    # will trigger only on ValueChangeEvent
            self.listen_event('My/MQTT/Topic', self.on_update, ValueUpdateEvent)    # will trigger only on ValueUpdateEvent

            # If you already have an item you can and should use the more convenient method of the item
            # to listen to the item events
            my_item = Item.get_item('MyItem')
            my_item.listen_event(self.on_change, ValueUpdateEvent)

        def on_change(self, event: ValueChangeEvent):
            assert isinstance(event, ValueChangeEvent), type(event)

        def on_update(self, event: ValueUpdateEvent):
            assert isinstance(event, ValueUpdateEvent), type(event)

    MyRule()

Additionally there is the possibility to filter not only on the event type but on the event values, too.
This can be achieved by passing an **instance** of EventFilter as event type.
There are convenience Filters (e.g. :class:`~HABApp.core.events.ValueUpdateEventFilter` and
:class:`~HABApp.core.events.ValueChangeEventFilter`) for the most used event types that provide type hints.



.. autoclass:: HABApp.core.events.EventFilter
   :members:

.. autoclass:: HABApp.core.events.ValueUpdateEventFilter
   :members:

.. autoclass:: HABApp.core.events.ValueChangeEventFilter
   :members:


.. exec_code::
    :hide_output:
    :caption: Example

    # ------------ hide: start ------------
    import time, HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.create_item('MyItem', HABApp.core.items.Item)
    # ------------ hide: stop -------------
    from HABApp import Rule
    from HABApp.core.events import EventFilter, ValueUpdateEventFilter, ValueUpdateEvent
    from HABApp.core.items import Item

    class MyRule(Rule):
        def __init__(self):
            super().__init__()
            my_item = Item.get_item('MyItem')

            # This will only call the callback for ValueUpdateEvents where the value==my_value
            my_item.listen_event(self.on_val_my_value, ValueUpdateEventFilter(value='my_value'))

            # This is the same as above but with the generic filter
            my_item.listen_event(self.on_val_my_value, EventFilter(ValueUpdateEvent, value='my_value'))

        def on_val_my_value(self, event: ValueUpdateEvent):
            assert isinstance(event, ValueUpdateEvent), type(event)

    MyRule()


Scheduler
------------------------------
With the scheduler it is easy to call functions in the future or periodically.
Do not use `time.sleep` but rather `self.run.at`.
Another very useful function is `self.run.countdown` as it can simplify many rules!

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Function
     - Description

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.soon`
     - Run the callback as soon as possible (typically in the next second).

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.at`
     - Run the callback in x seconds or at a specified time.

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.countdown`
     - Run a function after a time has run down

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.every`
     - Run a function periodically

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.every_minute`
     - Run a function every minute

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.every_hour`
     - Run a function every hour

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_every_day`
     - Run a function at a specific time every day

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_workdays`
     - Run a function at a specific time on workdays

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_weekends`
     - Run a function at a specific time on weekends

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_day_of_week`
     - Run a function at a specific time on specific days of the week

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_sun_dawn`
     - Run a function on dawn

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_sunrise`
     - Run a function on sunrise

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_sunset`
     - Run a function on sunset

   * - :meth:`~HABApp.rule.scheduler.HABAppSchedulerView.on_sun_dusk`
     - Run a function on dusk


All functions return an instance of ScheduledCallbackBase

.. autoclass:: HABApp.rule.scheduler.HABAppSchedulerView
   :members:
   :inherited-members:


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
        from .rule_a import ClassA      # type hints for the IDE

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
