
Getting Started
==================================

It is really recommended to use a python IDE, for example PyCharm.
The IDE can provide auto complete and static checks
which will help you write error free rules and vastly speed up your development.

First start HABApp and keep it running. It will automatically load and update all rules which
are created or changed in the configured ``rules`` directory.
Loading and unloading of rules can be observed in the HABApp logfile.

It is recommended to use HABApp from the console for these examples so the print output can be observed.

First rule
------------------------------
Rules are written as classes that inherit from :class:`HABApp.Rule`. Once the class gets instantiated the will run as
rules in the HABApp rule engine. So lets write a small rule which prints something.


.. exec_code::

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # ------------ hide: stop -------------
    import HABApp

    # Rules are classes that inherit from HABApp.Rule
    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # Use run.at to schedule things directly after instantiation,
            # don't do blocking things in __init__
            self.run.soon(self.say_something)

        def say_something(self):
            print('That was easy!')

    # Rules
    MyFirstRule()
    # ------------ hide: start ------------
    runner.process_events()
    runner.tear_down()
    # ------------ hide: stop -------------

A more generic rule
------------------------------
It is also possible to instantiate the rules with parameters.
This often comes in handy if there is some logic that shall be applied to different items.

.. exec_code::

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # ------------ hide: stop -------------
    import HABApp

    class MyFirstRule(HABApp.Rule):
        def __init__(self, my_parameter):
            super().__init__()
            self.param = my_parameter

            self.run.soon(self.say_something)

        def say_something(self):
            print(f'Param {self.param}')

    # This is normal python code, so you can create Rule instances as you like
    for i in range(2):
        MyFirstRule(i)
    for t in ['Text 1', 'Text 2']:
        MyFirstRule(t)
    # ------------ hide: start ------------
    runner.process_events()
    runner.tear_down()
    # ------------ hide: stop -------------


Interacting with items
------------------------------
HABApp uses an internal item registry to store both openHAB items and locally
created items (only visible within HABApp). Upon start-up HABApp retrieves
a list of openHAB items and adds them to the internal registry.
Rules and HABApp derived libraries may add additional local items which can be used
to share states across rules and/or files.

Access
""""""""""""""""""""""""""""""""""""""

An item is created and added to the item registry through the corresponding class factory method

.. exec_code::
   :hide_output:

   # ------------ hide: start ------------
   from rule_runner import SimpleRuleRunner
   SimpleRuleRunner().set_up()
   # ------------ hide: stop -------------

   from HABApp.core.items import Item

   # This will create an item in the local (HABApp) item registry
   item = Item.get_create_item("an-item-name", "a value")

Values
""""""""""""""""""""""""""""""""""""""

Posting values from the item will automatically create the events on the event bus.
This example will create an item in HABApp (locally) and post some updates to it.
To access items from openHAB use the correct openHAB item type (see :ref:`the openHAB item description <OPENHAB_ITEM_TYPES>`).

.. exec_code::

    # ------------ hide: start ------------
    import logging
    import sys
    root = logging.getLogger('HABApp')
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(name)15s] %(levelname)8s | %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.items import Item

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # Get the item or create it if it does not exist
            self.my_item = Item.get_create_item('Item_Name')

            self.run.soon(self.say_something)

        def say_something(self):
            # Post updates to the item through the internal event bus
            self.my_item.post_value('Test')
            self.my_item.post_value('Change')

            # The item value can be used in comparisons through this shortcut ...
            if self.my_item == 'Change':
                print('Item value is "Change"')
            # ... which is the same as this:
            if self.my_item.value == 'Change':
                print('Item.value is "Change"')


    MyFirstRule()
    # ------------ hide: start ------------
    runner.process_events()
    runner.tear_down()
    # ------------ hide: stop -------------


Timestamps
""""""""""""""""""""""""""""""""""""""

All items have two additional timestamps set which can be used to simplify rule logic.

* The time when the item was last updated
* The time when the item was last changed.


.. exec_code::

    # ------------ hide: start ------------
    from pendulum import DateTime
    from HABApp.core.items import Item
    from rule_runner import SimpleRuleRunner

    runner = SimpleRuleRunner()
    runner.set_up()

    item = Item.get_create_item('Item_Name', initial_value='old_value')
    item._last_update.dt = DateTime(2022, 8, 20, 12, 16)
    item._last_change.dt = DateTime(2022, 8, 20, 10, 30)

    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.items import Item

    class TimestampRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # This item was created by another rule, that's why "get_item" is used
            self.my_item = Item.get_item('Item_Name')

            # Access of timestamps
            print(f'Last update: {self.my_item.last_update}')
            print(f'Last change: {self.my_item.last_change}')

    TimestampRule()

    # ------------ hide: start ------------
    runner.tear_down()
    # ------------ hide: stop -------------



Watch items for events
------------------------------
It is possible to watch items for changes or updates.
The ``listen_event`` function takes an instance of ``EventFilter`` which describes the kind of event that will be
passed to the callback.


.. exec_code::

    # ------------ hide: start ------------
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()

    from HABApp.core.items import Item
    Item.get_create_item('Item_Name', initial_value='Some value')
    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.items import Item
    from HABApp.core.events import ValueUpdateEventFilter, ValueChangeEventFilter, ValueChangeEvent, ValueUpdateEvent

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # Get the item or create it if it does not exist
            self.my_item = Item.get_create_item('Item_Name')

            # Run this function whenever the item receives an ValueUpdateEvent
            self.listen_event(self.my_item, self.item_updated, ValueUpdateEventFilter())

            # If you already have an item you can use the more convenient method of the item
            # This is the recommended way to use the event listener
            self.my_item.listen_event(self.item_updated, ValueUpdateEventFilter())

            # Run this function whenever the item receives an ValueChangeEvent
            self.my_item.listen_event(self.item_changed, ValueChangeEventFilter())

        # the function has 1 argument which is the event
        def item_updated(self, event: ValueUpdateEvent):
            print(f'{event.name} updated value: "{event.value}"')
            print(f'Last update of {self.my_item.name}: {self.my_item.last_update}')

        def item_changed(self, event: ValueChangeEvent):
            print(f'{event.name} changed from "{event.old_value}" to "{event.value}"')
            print(f'Last change of {self.my_item.name}: {self.my_item.last_change}')


    MyFirstRule()
    # ------------ hide: start ------------
    i = Item.get_item('Item_Name')
    i.post_value('Changed value')
    runner.process_events()
    runner.tear_down()
    # ------------ hide: stop -------------

Trigger an event when an item is constant
------------------------------------------

.. exec_code::

    # ------------ hide: start ------------
    import time, HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.add_item(HABApp.core.items.Item('test_watch'))
    # ------------ hide: stop -------------

    import HABApp
    from HABApp.core.items import Item
    from HABApp.core.events import ItemNoChangeEvent

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # Get the item or create it if it does not exist
            self.my_item = Item.get_create_item('Item_Name')

            # This will create an event if the item is 10 secs constant
            watcher = self.my_item.watch_change(10)

            # this will automatically listen to the correct event
            watcher.listen_event(self.item_constant)

            # To listen to all ItemNoChangeEvent/ItemNoUpdateEvent independent of the timeout time use
            # self.listen_event(self.my_item, self.item_constant, watcher.EVENT)

        def item_constant(self, event: ItemNoChangeEvent):
            print(f'{event}')

    MyFirstRule()
    # ------------ hide: start ------------
    HABApp.core.EventBus.post_event('Item_Name', ItemNoChangeEvent('Item_Name', 10))
    runner.tear_down()
    # ------------ hide: stop -------------


Convenience functions
------------------------------------------

HABApp provides some convenience functions which make the rule creation easier and reduce boiler plate code.

post_value_if
""""""""""""""""""""""""""""""""""""""

``post_value_if`` will post a value to the item depending on its current state.
There are various comparisons available (see :meth:`documentation <HABApp.core.items.Item.post_value_if>`)
Something similar is available for openHAB items (``oh_post_update_if``)

.. exec_code::

    # ------------ hide: start ------------
    import time, HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.add_item(HABApp.core.items.Item('Item_Name'))
    # ------------ hide: stop -------------

    import HABApp
    from HABApp.core.items import Item

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # Get the item or create it if it does not exist
            self.my_item = Item.get_create_item('Item_Name')

            self.run.soon(self.say_something)

        def say_something(self):

            # This construct
            if self.my_item != 'overwrite value':
               self.my_item.post_value('Test')

            # ... is equivalent to
            self.my_item.pos_value_if('Test', equal='overwrite value')



    MyFirstRule()
    # ------------ hide: start ------------
    runner.process_events()
    runner.tear_down()
    # ------------ hide: stop -------------
