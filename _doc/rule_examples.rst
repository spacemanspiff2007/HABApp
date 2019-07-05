
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
    import time
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
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
