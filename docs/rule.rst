
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
Items from openHAB use the item name from openHAB and get created when HABApp successfully connects to
openHAB or when the openHAB configuration changes.
Items from MQTT use the topic as item name and get created as soon as a message gets processed.

Some item types provide convenience functions, so it is advised to always set the correct item type.

The preferred way to get and create items is through the class factories :class:`~HABApp.core.items.Item.get_item`
and :class:`~HABApp.core.items.Item.get_create_item` since this ensures the proper item class and provides type hints when
using an IDE!

.. exec_code::
    :caption: Example:
    :hide_output:

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    SimpleRuleRunner().set_up()
    # ------------ hide: stop ------------

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
    from rule_runner import SimpleRuleRunner
    SimpleRuleRunner().set_up()

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
:ref:`the openHAB item section <OPENHAB_ITEM_TYPES>` and the :ref:`the mqtt item section <MQTT_ITEM_TYPES>`

Interacting with events
------------------------------

It is possible to listen to events through the :meth:`~HABApp.Rule.listen_event` function.
The passed function will be called as soon as an event occurs and the event will pe passed as an argument
into the function.

There is the possibility to reduce the function calls to a certain event type with an additional event filter
(typically :class:`~HABApp.core.ValueUpdateEventFilter` or :class:`~HABApp.core.ValueChangeEventFilter`).

An overview over the events can be found on :ref:`the HABApp event section <HABAPP_EVENT_TYPES>`,
:ref:`the openHAB event section <OPENHAB_EVENT_TYPES>` and the :ref:`the MQTT event section <MQTT_EVENT_TYPES>`

.. exec_code::
    :hide_output:
    :caption: Example

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()

    import time, HABApp
    HABApp.core.Items.add_item(HABApp.core.items.Item('MyItem'))
    # ------------ hide: stop -------------
    from HABApp import Rule
    from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent, ValueChangeEventFilter, ValueUpdateEventFilter
    from HABApp.core.items import Item

    class MyRule(Rule):
        def __init__(self):
            super().__init__()
            self.listen_event('MyOpenhabItem', self.on_change, ValueChangeEventFilter())  # trigger only on ValueChangeEvent
            self.listen_event('My/MQTT/Topic', self.on_update, ValueUpdateEventFilter())  # trigger only on ValueUpdateEvent

            # If you already have an item you can and should use the more convenient method of the item
            # to listen to the item events
            my_item = Item.get_item('MyItem')
            my_item.listen_event(self.on_change, ValueUpdateEventFilter())

        def on_change(self, event: ValueChangeEvent):
            assert isinstance(event, ValueChangeEvent), type(event)

        def on_update(self, event: ValueUpdateEvent):
            assert isinstance(event, ValueUpdateEvent), type(event)

    MyRule()

Additionally there is the possibility to filter not only on the event type but on the event values, too.
This can be achieved by passing the value to the event filter.
There are convenience Filters (e.g. :class:`~HABApp.core.events.ValueUpdateEventFilter` and
:class:`~HABApp.core.events.ValueChangeEventFilter`) for the most used event types that provide type hints.


NoEventFilter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: HABApp.core.events.NoEventFilter
   :members:

EventFilter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: HABApp.core.events.EventFilter
   :members:

ValueUpdateEventFilter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: HABApp.core.events.ValueUpdateEventFilter
   :members:

ValueChangeEventFilter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: HABApp.core.events.ValueChangeEventFilter
   :members:

AndFilterGroup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: HABApp.core.events.AndFilterGroup
   :members:

OrFilterGroup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: HABApp.core.events.OrFilterGroup
   :members:


.. exec_code::
    :hide_output:
    :caption: Example

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()

    import time, HABApp
    HABApp.core.Items.add_item(HABApp.core.items.Item('MyItem'))
    # ------------ hide: stop -------------
    from HABApp import Rule
    from HABApp.core.events import EventFilter, ValueUpdateEventFilter, ValueUpdateEvent, OrFilterGroup
    from HABApp.core.items import Item

    class MyRule(Rule):
        def __init__(self):
            super().__init__()
            my_item = Item.get_item('MyItem')

            # This will only call the callback for ValueUpdateEvents where the value==my_value
            my_item.listen_event(self.on_val_my_value, ValueUpdateEventFilter(value='my_value'))

            # This is the same as above but with the generic filter
            my_item.listen_event(self.on_val_my_value, EventFilter(ValueUpdateEvent, value='my_value'))

            # trigger if the value is 1 or 2 by using both filters with or
            my_item.listen_event(
                self.value_1_or_2,
                OrFilterGroup(
                    ValueUpdateEventFilter(value=1), ValueUpdateEventFilter(value=2)
                )
            )

        def on_val_my_value(self, event: ValueUpdateEvent):
            assert isinstance(event, ValueUpdateEvent), type(event)

        def value_1_or_2(self, event: ValueUpdateEvent):
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




Other tools and scripts
------------------------------
HABApp provides convenience functions to run other tools and scripts. The working directory for the
new process is by default the folder of the HABApp configuration file.

Running tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
External tools can be run with the :meth:`~HABApp.Rule.execute_subprocess` function.
Once the process has finished the callback will be called with the captured output of the process.
Example::

    import HABApp

    class MyExecutionRule(HABApp.Rule):

        def __init__(self):
            super().__init__()

            self.execute_subprocess( self.func_when_finished, 'path_to_program', 'arg1_for_program')

        def func_when_finished(self, process_output: str):
            print(process_output)

    MyExecutionRule()


Running python scripts or modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Python scripts can be run with the :meth:`~HABApp.Rule.execute_python` function.
The working directory for a script is by default the folder of the script.
Once the script or module has finished the callback will be called with the captured output of the module/script.
Example::

    import HABApp

    class MyExecutionRule(HABApp.Rule):

        def __init__(self):
            super().__init__()

            self.execute_python( self.func_when_finished, '/path/to/python/script.py', 'arg1_for_script')

        def func_when_finished(self, module_output: str):
            print(module_output)

    MyExecutionRule()


FinishedProcessInfo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It's possible to get the raw process output instead of just the captured string. See
:meth:`~HABApp.Rule.execute_subprocess` or :meth:`~HABApp.Rule.execute_python` on how to enable it.

.. autoclass:: HABApp.rule.FinishedProcessInfo


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
   :var openhab: :ref:`openhab interaction <ref_openhab>`
   :var oh: short alias for :ref:`openhab <ref_openhab>`
