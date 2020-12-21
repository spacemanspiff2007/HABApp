
Getting Started
==================================
It is really recommended to use a python IDE, for example PyCharm.
The IDE can provide auto complete and static checks
which will help you write error free rules and vastly speed up your developement.

First start HABApp and keep it running. It will automatically load and update all rules which
are created or changed in the configured ``rules`` directory.
Loading and unloading of rules can be observed in the HABApp logfile.

It is recommended to use HABApp from the console for these examples so the print output can be observed.

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
HABApp uses a single dictionary to store both openhab items and locally
created items (only visible within HABApp). Upon start-up, HABApp retrieves
a list of openhab items through the REST API and put them in the dictionary
above. Rules and HABApp derived libraries may add additional local items. See
the next section for examples on how to do that.

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


Working with local items
~~~~~~~~~~~~~~~~~~~~~~~~~~
Local items are those that only exist in HABApp (i.e. they are not available
in openhab). There are useful for the following scenarios:

1. To share information between rules.
2. To simulate openhab items in unit tests.

The formmer affords the rules to not rely on additional global variables to
share states. The latter allows quick turn-around time for running the unit
tests.  In fact, the tests can be fully run within an IDE such as pycharm 
without needing open hab and HABapp running.

Create and add a generic item::
  item = HABApp.core.items.Item.get_create_item("an-item-name", "a value")
  " This will create an item and register it with the global item dict

In the majority of cases, we want to have strict typing on the item. This can
be done like this::
  item = HABApp.openhab.items.SwitchItem(name, HABApp.openhab.definitions.OnOffValue.ON)
  HABApp.core.Items.add_item(item)

To remove the above item from the global item dict::
  HABApp.core.Items.pop_item(item.name)

Changing a local item's value is also quite different compared to open hab
items. As the items are local, there is no command sent to the open hab REST
APIs. Also note that many item classes have helper methods that encapsulate the
commands being sent to open hab. These methods can't be used on local items.
Examples of them are ``SwitchItem::on(), SwithItem::off(), and DimmerItem.percentage()``.

Here are examples on how to change the value on local items::
  # no event is triggered when set_value is used.
  switchItem.set_value(HABApp.openhab.definitions.OnOffValue.ON)

  # an event will be created when post_value is used.
  dimmerItem.post_value(percentage)

Item equality
~~~~~~~~~~~~~~~
When coming over from the Java or jsr223 background, it is naturally to
compare items like this::
  if myItem == theOtherItem:
    # do something

That will most likely not achieve the intended result. The reason is because all
HABApp items (in package ``HABApp.openhab.items``) implement ``__eq__`` by
comparing the item's value / state and not the memory address. As such two
entirely different ``SwitchItem`` would be equals if their values are both 
``ON`` or ``OFF``. Here's how to properly do the comparison::
  if myItem is theOtherItem:
    # do something

  # or alternatively
  if myItem.name == theOtherItem.name::
    # do something

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

            # this will automatically listen to the correct event
            watcher.listen_event(self.item_constant)

            # To listen to multiple ItemNoChangeEvent/ItemNoUpdateEvents use
            # self.listen_event(self.my_item, self.item_constant, watcher.EVENT)

        def item_constant(self, event: ItemNoChangeEvent):
            print(f'{event}')

    MyFirstRule()
    # hide
    HABApp.core.EventBus.post_event('Item_Name', ItemNoChangeEvent('Item_Name', 10))
    runner.tear_down()
    # hide

