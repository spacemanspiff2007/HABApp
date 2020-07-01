
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

    class MyRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            my_item = Item.get_item('test_watch')

            my_item.watch_change(5)     # Create event when item doesn't change for  5 secs
            my_item.watch_change(10)    # Create event when item doesn't change for 10 secs

            # Listen to these events
            self.listen_event(my_item, self.item_constant, ItemNoChangeEvent)

            # Set the item to a value
            my_item.set_value('my_value')

        def item_constant(self, event):
            print(f'{event}')

    MyRule()
    # hide
    HABApp.core.EventBus.post_event('test_watch', ItemNoChangeEvent('test_watch', 5))
    HABApp.core.EventBus.post_event('test_watch', ItemNoChangeEvent('test_watch', 10))
    runner.tear_down()
    # hide


Process Errors in Rules
------------------------------------------
This example shows how to create a rule with a function which will be called when **any** rule throws an error.
The rule function then can push the error message to an openhab item or e.g. use Pushover to send the error message
to the mobile device (see :doc:`Avanced Usage <advanced_usage>` for more information).

.. execute_code::
    :ignore_stderr:

    # hide
    import datetime
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide

    import HABApp
    from HABApp.core.events.habapp_events import HABAppError

    class NotifyOnError(HABApp.Rule):
        def __init__(self):
            super().__init__()
            
            # Listen to all errors
            self.listen_event('HABApp.Errors', self.on_error, HABAppError)

        def on_error(self, error_event: HABAppError):
            msg = event.to_str() if isinstance(event, HABAppError) else event
            print(msg)

    NotifyOnError()


    # this is a faulty example. Do not create this part!
    class FaultyRule(HABApp.Rule):
        def __init__(self):
            super().__init__()
            self.run_soon(self.faulty_function)
        
        def faulty_function(self):
            1 / 0
    FaultyRule()
    # hide
    runner.process_events()
    runner.tear_down()
    # hide
