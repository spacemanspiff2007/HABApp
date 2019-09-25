.. module:: HABApp.util


util - rule creation utilities
==================================

The util package contains useful classes which make rule creation easier.


Counter
------------------------------

Example
^^^^^^^^^^^^^^^^^^
.. execute_code::

    # hide
    from HABApp.util import Counter
    # hide

    def print_value(val):
        print( f'Counter is {val}')

    c = Counter( initial_value=5, on_change=print_value)
    c.increase()
    c.decrease()

Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: Counter
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

MultiMode
------------------------------
Prioritizer which automatically switches between values with different priorities.
Very useful when different states or modes overlap, e.g. automatic and manual mode. etc.

Example
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

            item = self.get_item(f'MultiModeTestItem', MultiModeItem)
            self.listen_event(item, self.item_update, ValueNoChangeEvent)

            item.create_mode('Automatic', 0, initial_value=5)
            item.create_mode('Manual', 10, initial_value=0)

            print('disable/enable higher priority')
            item.get_mode('manual').set_enabled(False)
            item.get_mode('manual').set_value(10)

            print('\nset value lower priority')
            item.get_mode('automatic').set_value(55)

            print('disable higher priority')
            item.get_mode('manual').set_enabled(False)

            print('\nautomatically disable mode')
            # it is possible to automatically disable a mode
            # this will disable the manual mode if the automatic mode sets a value greater equal manual mode
            item.get_mode('Automatic').set_value(5)
            item.get_mode('manual').set_value(10)

            item.get_mode('manual').auto_disable_on = '>='

            item.get_mode('Automatic').set_value(11)    # manual now gets disabled because the lower priority value is >= itself
            item.get_mode('Automatic').set_value(4)

            print('\nuse of functions')
            # It is possible to use functions to calculate the new value for a mode.
            # E.g. shutter control and the manual mode moves the shades. If it's dark the automatic mode closes the shutter again.
            # This could be achievied by automatically disable the manual mode or if the state should be remembered then
            # the max function should be used
            item.create_mode('Manual', 10, initial_value=5, calc_value_func=max)    # this will overwrite the earlier declaration
            item.get_mode('Automatic').set_value(7)
            item.get_mode('Automatic').set_value(3)

        def item_update(self, event):
            print(f'State: {event.state}')

    MyMultiModeItemTestRule()
    # hide
    runner.tear_down()
    # hide



Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: MultiModeItem
   :members:

.. autoclass:: HABApp.util.multi_value.MultiModeValue
   :members:

