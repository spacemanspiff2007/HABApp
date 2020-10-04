
Getting Started
==================================
It is really recommended to use a python IDE, for example PyCharm.
The IDE can provide auto complete and static checks
which will help you write error free rules and vastly speed up your developement.

First start HABApp. When it is running it will automatically load and update all rules which
are created in the configured ``rules`` directory.
Loading and unloading of rules can be observed in the HABApp logfile.

First rule
------------------------------
Rules are written as classes that inherit from :class:`HABApp.Rule`. Once the class gets instantiated the will run as
rules in the HABApp rule engine. So lets write a small rule which prints something.


.. execute_code::

    # hide
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide
    import HABApp

    # Rules are classes that inherit from HABApp.Rule
    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # Use run_soon to schedule things directly after instantiation,
            # don't do blocking things in __init__
            self.run_soon(self.say_something)

        def say_something(self):
            print('That was easy!')

    # Rules
    MyFirstRule()
    # hide
    runner.process_events()
    runner.tear_down()
    # hide

A more generic rule
------------------------------
It is also possible to instantiate the rules with parameters.
This often comes in handy if there is some logic that shall be applied to different items.

.. execute_code::

    # hide
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide
    import HABApp

    class MyFirstRule(HABApp.Rule):
        def __init__(self, my_parameter):
            super().__init__()
            self.param = my_parameter

            self.run_soon(self.say_something)

        def say_something(self):
            print(f'Param {self.param}')

    # This is normal python code, so you can create Rule instances as you like
    for i in range(2):
        MyFirstRule(i)
    for t in ['Text 1', 'Text 2']:
        MyFirstRule(t)
    # hide
    runner.process_events()
    runner.tear_down()
    # hide


Interacting with items
------------------------------
Iterating with items is done through the corresponding Item factory methods.
Posting values will automatically create the events on the event bus.
This example will create an item in HABApp (locally) and post some updates to it.
To access items from openhab use the correct openhab item type (see :ref:`the openhab item description <OPENHAB_ITEM_TYPES>`).

.. execute_code::
    :header_output: Output

    # hide
    import logging
    import sys
    root = logging.getLogger('HABApp')
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(name)15s] %(levelname)8s | %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide
    import HABApp
    from HABApp.core.items import Item

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # Get the item or create it if it does not exist
            self.my_item = Item.get_create_item('Item_Name')

            self.run_soon(self.say_something)

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
    # hide
    runner.process_events()
    runner.tear_down()
    # hide



Watch items for events
------------------------------
It is possible to watch items for changes or updates.


.. execute_code::

    # hide
    from HABApp.core.items import Item
    Item.get_create_item('Item_Name', initial_value='Some value')

    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide
    import HABApp
    from HABApp.core.items import Item
    from HABApp.core.events import ValueUpdateEvent, ValueChangeEvent

    class MyFirstRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            # Get the item or create it if it does not exist
            self.my_item = Item.get_create_item('Item_Name')

            # Run this function whenever the item receives an ValueUpdateEvent
            self.listen_event(self.my_item, self.item_updated, ValueUpdateEvent)

            # Run this function whenever the item receives an ValueChangeEvent
            self.listen_event(self.my_item, self.item_changed, ValueChangeEvent)

            # If you already have an item you can use the more convenient method of the item
            self.my_item.listen_event(self.item_changed, ValueChangeEvent)

        # the function has 1 argument which is the event
        def item_changed(self, event: ValueChangeEvent):
            print(f'{event.name} changed from "{event.old_value}" to "{event.value}"')
            print(f'Last change of {self.my_item.name}: {self.my_item.last_change}')

        def item_updated(self, event: ValueUpdateEvent):
            print(f'{event.name} updated value: "{event.value}"')
            print(f'Last update of {self.my_item.name}: {self.my_item.last_update}')

    MyFirstRule()
    # hide
    i = Item.get_create_item('Item_Name')
    i.post_value('Changed value')
    runner.process_events()
    runner.tear_down()
    # hide

Trigger an event when an item is constant
------------------------------------------

.. execute_code::

    # hide
    import time, HABApp
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.create_item('test_watch', HABApp.core.items.Item)
    # hide

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

            # use .EVENT to always listen to the correct event
            self.listen_event(self.my_item, self.item_constant, watcher.EVENT)

        def item_constant(self, event: ItemNoChangeEvent):
            print(f'{event}')

    MyFirstRule()
    # hide
    HABApp.core.EventBus.post_event('Item_Name', ItemNoChangeEvent('Item_Name', 10))
    runner.tear_down()
    # hide

