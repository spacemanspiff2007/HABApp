
Additional rule examples
==================================

Using the scheduler
--------------------
.. literalinclude:: ../conf/rules/time_rule.py


Mirror openHAB events to a MQTT Broker
---------------------------------------
.. literalinclude:: ../conf/rules/openhab_to_mqtt_rule.py

.. _item_const_example:

Trigger an event when an item is constant
------------------------------------------
Get an even when the item is constant for 5 and for 10 seconds.

.. exec_code::

    # ------------ hide: start ------------
    import time, HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.create_item('test_watch', HABApp.core.items.Item)
    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.items import Item
    from HABApp.core.events import ItemNoChangeEvent

    class MyRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            my_item = Item.get_item('test_watch')

            # Create an event when the item doesn't change for 5 secs and
            # create a watcher for ItemNoChangeEvent with 5s const time
            my_item.watch_change(5).listen_event(self.item_constant_5s)

            # Just create an event when the item doesn't change for 10 secs
            my_item.watch_change(10)

            # Listen to all ItemNoChangeEvents for the item
            my_item.listen_event(self.item_constant, ItemNoChangeEvent)

            # Set the item to a value to generate the ItemNoChangeEvent events
            my_item.set_value('my_value')

        def item_constant_5s(self, event):
            print(f'Item 5s const: {event}')

        def item_constant(self, event):
            print(f'Item const: {event}')

    MyRule()
    # ------------ hide: start ------------
    HABApp.core.EventBus.post_event('test_watch', ItemNoChangeEvent('test_watch', 5))
    HABApp.core.EventBus.post_event('test_watch', ItemNoChangeEvent('test_watch', 10))
    runner.tear_down()
    # ------------ hide: stop -------------


Turn something off after movement
------------------------------------------
Turn a device off 30 seconds after one of the movement sensors in a room signals movement.


.. exec_code::
    :hide_output:

    # ------------ hide: start ------------
    import time, HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.create_item('movement_sensor1', HABApp.core.items.Item)
    HABApp.core.Items.create_item('movement_sensor2', HABApp.core.items.Item)
    HABApp.core.Items.create_item('my_device', HABApp.core.items.Item)
    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.items import Item
    from HABApp.core.events import ValueUpdateEvent

    class MyCountdownRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            self.countdown = self.run.countdown(30, self.switch_off)
            self.device = Item.get_item('my_device')

            self.movement1 = Item.get_item('movement_sensor1')
            self.movement1.listen_event(self.movement, ValueUpdateEvent)

            self.movement2 = Item.get_item('movement_sensor2')
            self.movement2.listen_event(self.movement, ValueUpdateEvent)

        def movement(self, event: ValueUpdateEvent):
            if self.device != 'ON':
                self.device.post_value('ON')

            self.countdown.reset()

        def switch_off(self):
            self.device.post_value('OFF')

    MyCountdownRule()
    # ------------ hide: start ------------
    runner.tear_down()
    # ------------ hide: stop -------------

Process Errors in Rules
------------------------------------------
This example shows how to create a rule with a function which will be called when **any** rule throws an error.
The rule function then can push the error message to an openhab item or e.g. use Pushover to send the error message
to the mobile device (see :doc:`Avanced Usage <advanced_usage>` for more information).

.. exec_code::

    # ------------ hide: start ------------
    import datetime
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # ------------ hide: stop -------------

    import HABApp
    from HABApp.core.events.habapp_events import HABAppException

    class NotifyOnError(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # Listen to all errors
            self.listen_event('HABApp.Errors', self.on_error, HABAppException)

        def on_error(self, error_event: HABAppException):
            msg = event.to_str() if isinstance(event, HABAppException) else event
            print(msg)

    NotifyOnError()


    # this is a faulty example. Do not create this part!
    class FaultyRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            self.run.soon(self.faulty_function)

        def faulty_function(self):
            1 / 0
    FaultyRule()
    # ------------ hide: start ------------
    runner.process_events()
    runner.tear_down()
    # ------------ hide: stop -------------
