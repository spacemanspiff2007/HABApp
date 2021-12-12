.. module:: HABApp.util


util - helpers and utilities
==================================

The util package contains useful classes which make rule creation easier.

Functions
------------------------------

min
^^^^^^^^^^^^^^^^^^

This function is very useful together with the all possible functions of :class:`~HABApp.util.multimode.ValueMode` for the
:class:`~HABApp.util.multimode.MultiModeItem`.
For example it can be used to automatically disable or calculate the new value of the :class:`~HABApp.util.multimode.ValueMode`
It behaves like the standard python function except that it will ignore ``None`` values which are sometimes set as the item state.

.. exec_code::
    :hide_output:

    from HABApp.util.functions import min

    print(min(1, 2, None))

.. autofunction:: HABApp.util.functions.min


max
^^^^^^^^^^^^^^^^^^

This function is very useful together with the all possible functions of :class:`~HABApp.util.multimode.ValueMode` for the
:class:`~HABApp.util.multimode.MultiModeItem`.
For example it can be used to automatically disable or calculate the new value of the :class:`~HABApp.util.multimode.ValueMode`
It behaves like the standard python function except that it will ignore ``None`` values which are sometimes set as the item state.

.. exec_code::
    :hide_output:

    from HABApp.util.functions import max

    print(max(1, 2, None))

.. autofunction:: HABApp.util.functions.max


rgb_to_hsb
^^^^^^^^^^^^^^^^^^

Converts a rgb value to hsb color space

.. exec_code::
    :hide_output:

    from HABApp.util.functions import rgb_to_hsb

    print(rgb_to_hsb(224, 201, 219))

.. autofunction:: HABApp.util.functions.rgb_to_hsb


hsb_to_rgb
^^^^^^^^^^^^^^^^^^

Converts a hsb value to the rgb color space

.. exec_code::
    :hide_output:

    from HABApp.util.functions import hsb_to_rgb

    print(hsb_to_rgb(150, 40, 100))

.. autofunction:: HABApp.util.functions.hsb_to_rgb


CounterItem
------------------------------

Example
^^^^^^^^^^^^^^^^^^
.. exec_code::

    from HABApp.util import CounterItem
    c = CounterItem.get_create_item('MyCounter', initial_value=5)
    print(c.increase())
    print(c.decrease())
    print(c.reset())

Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: CounterItem
   :members:

   .. automethod:: __init__


Statistics
------------------------------

Example
^^^^^^^^^^^^^^^^^^
.. exec_code::

    # ------------ hide: start ------------
    from HABApp.util import Statistics
    # ------------ hide: stop -------------
    s = Statistics(max_samples=4)
    for i in range(1,4):
        s.add_value(i)
        print(s)


Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: Statistics
   :members:

EventListenerGroup
------------------------------
EventListenerGroup is a helper class which allows to subscribe to multiple items at once.
All subscriptions can be canceled together, too.
This is useful if e.g. something has to be done once after a sensor reports a value.

Example
^^^^^^^^^^^^^^^^^^
This is a rule which will turn on the lights once (!) in a room on the first movement in the morning.
The lights will only turn on after 4 and before 8 and two movement sensors are used to pick up movement.


.. exec_code::

    # ------------ hide: start ------------
    import HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.add_item(HABApp.openhab.items.SwitchItem('RoomLights'))
    HABApp.core.Items.add_item(HABApp.openhab.items.NumberItem('MovementSensor1'))
    HABApp.core.Items.add_item(HABApp.openhab.items.NumberItem('MovementSensor2'))
    # ------------ hide: stop -------------
    from datetime import time

    from HABApp import Rule
    from HABApp.core.events import ValueChangeEvent
    from HABApp.openhab.items import SwitchItem, NumberItem
    from HABApp.util import EventListenerGroup


    class EventListenerGroupExample(Rule):
        def __init__(self):
            super().__init__()
            self.lights = SwitchItem.get_item('RoomLights')
            self.sensor_move_1 = NumberItem.get_item('MovementSensor1')
            self.sensor_move_2 = NumberItem.get_item('MovementSensor2')

            # use the defaults so we don't have to pass the callback and event filter in add_listener
            self.group = EventListenerGroup().add_listener(
                [self.sensor_move_1, self.sensor_move_2], self.sensor_changed, ValueChangeEvent)

            self.run.on_every_day(time(4), self.listen_sensors)
            self.run.on_every_day(time(8), self.sensors_cancel)

        def listen_sensors(self):
            self.listeners.listen()

        def sensors_cancel(self):
            self.listeners.cancel()

        def sensor_changed(self, event):
            self.listeners.cancel()
            self.lights.on()


    EventListenerGroupExample()


.. autoclass:: EventListenerGroup
   :members:

MultiModeItem
------------------------------
Prioritizer item which automatically switches between values with different priorities.
Very useful when different states or modes overlap, e.g. automatic and manual mode. etc.

Basic Example
^^^^^^^^^^^^^^^^^^
.. exec_code::

    # ------------ hide: start ------------
    import HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.events import ValueUpdateEvent
    from HABApp.util.multimode import MultiModeItem, ValueMode

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem
            item = MultiModeItem.get_create_item('MultiModeTestItem')
            item.listen_event(self.item_update, ValueUpdateEvent)

            # create two different modes which we will use and add them to the item
            auto = ValueMode('Automatic', initial_value=5)
            manu = ValueMode('Manual', initial_value=0)
            item.add_mode(0, auto).add_mode(10, manu)

            # This shows how to enable/disable a mode and how to get a mode from the item
            print('disable/enable the higher priority mode')
            item.get_mode('manual').set_enabled(False)  # disable mode
            item.get_mode('manual').set_value(11)       # setting a value will enable it again

            # This shows that changes of the lower priority is only show when
            # the mode with the higher priority gets disabled
            print('')
            print('Set value of lower priority')
            auto.set_value(55)
            print('Disable higher priority')
            manu.set_enabled(False)

        def item_update(self, event):
            print(f'State: {event.value}')

    MyMultiModeItemTestRule()
    # ------------ hide: start ------------
    runner.tear_down()
    # ------------ hide: stop -------------

Advanced Example
^^^^^^^^^^^^^^^^^^
.. exec_code::

    # ------------ hide: start ------------
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
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    # ------------ hide: stop -------------
    import logging
    import HABApp
    from HABApp.core.events import ValueUpdateEvent
    from HABApp.util.multimode import MultiModeItem, ValueMode

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem
            item = MultiModeItem.get_create_item('MultiModeTestItem')
            item.listen_event(self.item_update, ValueUpdateEvent)

            # helper to print the heading so we have a nice outpt
            def print_heading(_heading):
                print('')
                print('-' * 80)
                print(_heading)
                print('-' * 80)
                for p, m in item.all_modes():
                    print(f'Prio {p:2d}: {m}')
                print('')


            log = logging.getLogger('AdvancedMultiMode')

            # create modes and add them
            auto = ValueMode('Automatic', initial_value=5, logger=log)
            manu = ValueMode('Manual', initial_value=10, logger=log)
            item.add_mode(0, auto).add_mode(10, manu)


            # it is possible to automatically disable a mode
            # this will disable the manual mode if the automatic mode
            # sets a value greater equal manual mode
            print_heading('Automatically disable mode')

            # A custom function can also disable the mode:
            manu.auto_disable_func = lambda low, own: low >= own

            auto.set_value(11) # <-- manual now gets disabled because
            auto.set_value(4)  #     the lower priority value is >= itself


            # It is possible to use functions to calculate the new value for a mode.
            # E.g. shutter control and the manual mode moves the shades. If it's dark the automatic
            # mode closes the shutter again. This could be achievied by automatically disable the
            # manual mode or if the state should be remembered then the max function should be used

            # create a move and use the max function for output calculation
            manu = ValueMode('Manual', initial_value=5, logger=log, calc_value_func=max)
            item.add_mode(10, manu)    # overwrite the earlier added mode

            print_heading('Use of functions')

            auto.set_value(7)   # manu uses max, so the value from auto is used
            auto.set_value(3)

        def item_update(self, event):
            print(f'Item value: {event.value}')

    MyMultiModeItemTestRule()
    # ------------ hide: start ------------
    runner.tear_down()
    # ------------ hide: stop -------------


Example SwitchItemValueMode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The SwitchItemMode is same as ValueMode but enabled/disabled of the mode is controlled by a OpenHAB
:class:`~HABApp.openhab.items.SwitchItem`. This is very useful if the mode shall be deactivated from the OpenHAB sitemaps.

.. exec_code::

    # ------------ hide: start ------------
    import HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()

    from HABApp.openhab.items import SwitchItem
    HABApp.core.Items.add_item(SwitchItem('Automatic_Enabled', initial_value='ON'))
    # ------------ hide: stop -------------
    import HABApp
    from HABApp.core.events import ValueUpdateEvent
    from HABApp.openhab.items import SwitchItem
    from HABApp.util.multimode import MultiModeItem, SwitchItemValueMode, ValueMode

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem
            item = MultiModeItem.get_create_item('MultiModeTestItem')

            # this switch allows to enable/disable the mode
            switch = SwitchItem.get_item('Automatic_Enabled')
            print(f'Switch is {switch}')

            # this is how the switch gets linked to the mode
            # if the switch is on, the mode is on, too
            mode = SwitchItemValueMode('Automatic', switch)
            print(mode)

            # Use invert_switch if the desired behaviour is
            # if the switch is off, the mode is on
            mode = SwitchItemValueMode('AutomaticOff', switch, invert_switch=True)
            print(mode)

            # This shows how the SwitchItemValueMode can be used to disable any logic except for the manual mode.
            # Now everything can be enabled/disabled from the openhab sitemap
            item.add_mode(100, mode)
            item.add_mode(101, ValueMode('Manual'))

    MyMultiModeItemTestRule()
    # ------------ hide: start ------------
    runner.tear_down()
    # ------------ hide: stop -------------


Documentation
^^^^^^^^^^^^^^^^^^^^^^

MultiModeItem
"""""""""""""""""""""""""
.. autoclass:: HABApp.util.multimode.MultiModeItem
   :members:

ValueMode
"""""""""""""""""""""""""
.. autoclass:: HABApp.util.multimode.ValueMode
   :members:
   :inherited-members:

SwitchItemValueMode
"""""""""""""""""""""""""
.. autoclass:: HABApp.util.multimode.SwitchItemValueMode
   :members:
   :inherited-members:
