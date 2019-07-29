
Additional rule examples
==================================

Using the scheduler
--------------------
.. literalinclude:: ../conf/rules/time_rule.py


Mirror openHAB events to a MQTT Broker
---------------------------------------
.. literalinclude:: ../conf/rules/openhab_to_mqtt_rule.py

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
    from HABApp.core.events import ValueNoChangeEvent

    class MyRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            self.item_watch('test_watch', 5)
            self.item_watch('test_watch', 10)
            self.listen_event('test_watch', self.item_constant, ValueNoChangeEvent)

            self.set_item_state('test_watch', 'my_value')

        def item_constant(self, event):
            print(f'{event}')

    MyRule()
    # hide
    HABApp.core.EventBus.post_event('test_watch', ValueNoChangeEvent('test_watch', 'my_value', 5))
    HABApp.core.EventBus.post_event('test_watch', ValueNoChangeEvent('test_watch', 'my_value', 10))
    runner.tear_down()
    # hide


Register a callback for errors
------------------------------------------
This example shows how to create a rule with a function which will be called when **any** rule throws an error.
The rule function then can push the error message to an openhab item or e.g. use Pushover to send the error message to the mobile device.

.. execute_code::
    :ignore_stderr:

    # hide
    import datetime
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide

    import HABApp
    from HABApp.core import WrappedFunction

    class NotifyOnError(HABApp.Rule):
        def __init__(self):
            super().__init__()
            
            # so it get's unloaded propperly in case we make changes to this rule
            self.register_on_unload(WrappedFunction.CLEAR_ERROR_CALLBACK)

            # register function 
            WrappedFunction.REGISTER_ERROR_CALLBACK(self.on_error)
            
        def on_error(self, error_message: str):
            print(f'Message:\n{error_message}\n')

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
    runner.process_events(datetime.datetime.now())
    runner.tear_down()
    # hide
