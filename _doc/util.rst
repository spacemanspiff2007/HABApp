.. module:: HABApp.util


util - helpers and utilities
==================================

The util package contains useful classes which make rule creation easier.


Counter
------------------------------

Example
^^^^^^^^^^^^^^^^^^
.. execute_code::

    from HABApp.util import CounterItem
    c = CounterItem.get_create_item('MyCounter', initial_value=5)
    print(c.increase())
    print(c.decrease())

Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: CounterItem
   :members:

   .. automethod:: __init__


Statistics
------------------------------

Example
^^^^^^^^^^^^^^^^^^
.. execute_code::

    # hide
    from HABApp.util import Statistics
    # hide

    s = Statistics(max_samples=4)
    for i in range(1,4):
        s.add_value(i)
        print(s)


Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: Statistics
   :members:

   .. automethod:: __init__

MultiModeItem
------------------------------
Prioritizer item which automatically switches between values with different priorities.
Very useful when different states or modes overlap, e.g. automatic and manual mode. etc.

Basic Example
^^^^^^^^^^^^^^^^^^
.. execute_code::

    # hide
    import HABApp
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide

    import HABApp
    from HABApp.core.events import ValueUpdateEvent
    from HABApp.util import MultiModeItem

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem
            item = MultiModeItem.get_create_item('MultiModeTestItem')
            self.listen_event(item, self.item_update, ValueUpdateEvent)

            # create two different modes which we will use
            item.create_mode('Automatic', 0, initial_value=5)
            item.create_mode('Manual', 10, initial_value=0)

            # This shows how to enable/disable a mode
            print('disable/enable the higher priority mode')
            item.get_mode('manual').set_enabled(False)
            item.get_mode('manual').set_value(11)

            # This shows that changes of the lower priority only show when
            # the mode with the higher priority gets disabled
            print('')
            print('Set value of lower priority')
            item.get_mode('automatic').set_value(55)
            print('Disable higher priority')
            item.get_mode('manual').set_enabled(False)

        def item_update(self, event):
            print(f'State: {event.value}')

    MyMultiModeItemTestRule()
    # hide
    runner.tear_down()
    # hide

Advanced Example
^^^^^^^^^^^^^^^^^^
.. execute_code::

    # hide
    import logging
    import sys
    root = logging.getLogger('AdvancedMultiMode')
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(name)17s] %(levelname)8s | %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


    import HABApp
    from tests import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # hide

    import logging
    import HABApp
    from HABApp.core.events import ValueUpdateEvent
    from HABApp.util import MultiModeItem

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem and assign logger
            log = logging.getLogger('AdvancedMultiMode')
            item = MultiModeItem.get_create_item('MultiModeTestItem', log)
            self.listen_event(item, self.item_update, ValueUpdateEvent)

            # create two different modes which we will use
            item.create_mode('Automatic', 2, initial_value=5)
            item.create_mode('Manual', 10).set_value(10)
            print(f'{repr(item.get_mode("Automatic"))}')
            print(f'{repr(item.get_mode("Manual"))}')


            # it is possible to automatically disable a mode
            # this will disable the manual mode if the automatic mode
            # sets a value greater equal manual mode
            print('')
            print('-' * 80)
            print('Automatically disable mode')
            print('-' * 80)
            item.get_mode('manual').auto_disable_on = '>='  # disable when low priority value >= mode value

            item.get_mode('Automatic').set_value(11)    # <-- manual now gets disabled because
            item.get_mode('Automatic').set_value(4)     #     the lower priority value is >= itself


            # It is possible to use functions to calculate the new value for a mode.
            # E.g. shutter control and the manual mode moves the shades. If it's dark the automatic
            # mode closes the shutter again. This could be achievied by automatically disable the
            # manual mode or if the state should be remembered then the max function should be used
            print('')
            print('-' * 80)
            print('Use of functions')
            print('-' * 80)
            item.create_mode('Manual', 10, initial_value=5, calc_value_func=max)    # overwrite the earlier declaration
            item.get_mode('Automatic').set_value(7)
            item.get_mode('Automatic').set_value(3)

        def item_update(self, event):
            print(f'State: {event.value}')

    MyMultiModeItemTestRule()
    # hide
    runner.tear_down()
    # hide



Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: MultiModeItem
   :members:

.. autoclass:: HABApp.util.multimode_item.MultiModeValue
   :members:

