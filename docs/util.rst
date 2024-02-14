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


.. _RATE_LIMITER:


Rate limiter
------------------------------
A simple rate limiter implementation which can be used in rules.
The limiter is not rule bound so the same limiter can be used in multiples files.
It also works as expected across rule reloads.


Defining limits
^^^^^^^^^^^^^^^^^^
Limits can either be explicitly added or through a textual description.
If the limit does already exist it will not be added again.
It's possible to explicitly create the limits or through some small textual description with the following syntax:

.. code-block:: text

    [count] [per|in|/] [count (optional)] [s|sec|second|m|min|minute|hour|h|day|month|year] [s (optional)]

Whitespaces are ignored and can be added as desired

Examples:

* ``5 per minute``
* ``20 in 15 mins``
* ``300 / hour``


Fixed window elastic expiry algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This algorithm implements a fixed window with elastic expiry.
That means if the limit is hit the interval time will be increased by the expiry time.

For example ``3 per minute``:

* First hit comes ``00:00:00``. Two more hits at ``00:00:59``.
  All three pass, intervall goes from ``00:00:00`` - ``00:01:00``.
  Another hit comes at ``00:01:01`` an passes. The intervall now goes from ``00:01:01`` - ``00:02:01``.

* First hit comes ``00:00:00``. Two more hits at ``00:00:30``. All three pass.
  Another hit comes at ``00:00:45``, which gets rejected and the intervall now goes from ``00:00:00`` - ``00:01:45``.
  A rejected hit makes the interval time longer by expiry time. If another hit comes at ``00:01:30`` it
  will also get rejected and the intervall now goes from ``00:00:00`` - ``00:02:30``.


Leaky bucket algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The leaky bucket algorithm is based on the analogy of a bucket that leaks at a constant rate.
As long as the bucket is not full the hits will pass. If the bucket overflows the hits will get rejected.
Since the bucket leaks at a constant rate it will gradually get empty again thus allowing hits to pass again.


Example
^^^^^^^^^^^^^^^^^^

.. exec_code::

    from HABApp.util import RateLimiter

    # Create or get existing, name is case insensitive
    limiter = RateLimiter('MyRateLimiterName')

    # define limits, duplicate limits of the same algorithm will only be added once
    # These lines all define the same limit so it'll result in only one limiter added
    limiter.add_limit(5, 60)   # add limits explicitly
    limiter.parse_limits('5 per minute').parse_limits('5 in 60s', '5/60seconds')  # add limits through text

    # add additional limit with leaky bucket algorithm
    limiter.add_limit(10, 100, algorithm='leaky_bucket')

    # add additional limit with fixed window elastic expiry algorithm
    limiter.add_limit(10, 100, algorithm='fixed_window_elastic_expiry')

    # Test the limit without increasing the hits
    for _ in range(100):
        assert limiter.test_allow()

    # the limiter will allow 5 calls ...
    for _ in range(5):
        assert limiter.allow()

    # and reject the 6th
    assert not limiter.allow()

    # It's possible to get statistics about the limiter and the corresponding windows
    print(limiter.info())

    # There is a counter that keeps track of the total skips that can be reset
    print('Counter:')
    print(limiter.total_skips)
    limiter.reset()     # Can be reset
    print(limiter.total_skips)


Recommendation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Limiting external requests to an external API works well with the leaky bucket algorithm (maybe with some initial hits).
For limiting notifications the best results can be achieved by combining both algorithms.
Fixed window elastic expiry will notify but block until an issue is resolved,
that's why it's more suited for small intervals. Leaky bucket will allow hits even while the issue persists,
that's why it's more suited for larger intervals.

.. exec_code::

    from HABApp.util import RateLimiter

    limiter = RateLimiter('MyNotifications')
    limiter.parse_limits('5 in 1 minute', algorithm='fixed_window_elastic_expiry')
    limiter.parse_limits("20 in 1 hour", algorithm='leaky_bucket')


Documentation
^^^^^^^^^^^^^^^^^^
.. autofunction:: HABApp.util.RateLimiter


.. autoclass:: HABApp.util.rate_limiter.limiter.Limiter
   :members:
   :inherited-members:

.. autoclass:: HABApp.util.rate_limiter.limiter.LimiterInfo
   :members:
   :inherited-members:

.. autoclass:: HABApp.util.rate_limiter.limiter.FixedWindowElasticExpiryLimitInfo
   :members:
   :inherited-members:

.. autoclass:: HABApp.util.rate_limiter.limiter.LeakyBucketLimitInfo
   :members:
   :inherited-members:


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

Fade
------------------------------
Fade is a helper class which allows to easily fade a value up or down.

Example
^^^^^^^^^^^^^^^^^^
This example shows how to fade a Dimmer from 0 to 100 in 30 secs


.. exec_code::

    # ------------ hide: start ------------
    import HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.add_item(HABApp.openhab.items.DimmerItem('Dimmer1'))
    # ------------ hide: stop -------------

    from HABApp import Rule
    from HABApp.openhab.items import DimmerItem
    from HABApp.util import Fade

    class FadeExample(Rule):
        def __init__(self):
            super().__init__()
            self.dimmer = DimmerItem.get_item('Dimmer1')
            self.fade = Fade(callback=self.fade_value)  # self.dimmer.percent would also be a good callback in this example

            # Setup the fade and schedule its execution
            # Fade from 0 to 100 in 30s
            self.fade.setup(0, 100, 30).schedule_fade()

        def fade_value(self, value):
            self.dimmer.percent(value)

    FadeExample()


This example shows how to fade three values together (e.g. for an RGB strip)


.. exec_code::

    # ------------ hide: start ------------
    import HABApp
    from rule_runner import SimpleRuleRunner
    runner = SimpleRuleRunner()
    runner.set_up()
    HABApp.core.Items.add_item(HABApp.openhab.items.DimmerItem('Dimmer1'))
    # ------------ hide: stop -------------

    from HABApp import Rule
    from HABApp.openhab.items import DimmerItem
    from HABApp.util import Fade

    class Fade3Example(Rule):
        def __init__(self):
            super().__init__()
            self.fade1 = Fade(callback=self.fade_value)
            self.fade2 = Fade()
            self.fade3 = Fade()

            # Setup the fades and schedule the execution of one fade where the value gets updated every sec
            self.fade3.setup(0, 100, 30)
            self.fade2.setup(0, 50, 30)
            self.fade1.setup(0, 25, 30, min_step_duration=1).schedule_fade()

        def fade_value(self, value):
            value1 = value
            value2 = self.fade2.get_value()
            value3 = self.fade3.get_value()

    Fade3Example()

Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: Fade
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
    from HABApp.core.events import ValueChangeEventFilter
    from HABApp.openhab.items import SwitchItem, NumberItem
    from HABApp.util import EventListenerGroup


    class EventListenerGroupExample(Rule):
        def __init__(self):
            super().__init__()
            self.lights = SwitchItem.get_item('RoomLights')
            self.sensor_move_1 = NumberItem.get_item('MovementSensor1')
            self.sensor_move_2 = NumberItem.get_item('MovementSensor2')

            # use a list of items which will be subscribed with the same callback and event
            self.listeners = EventListenerGroup().add_listener(
                [self.sensor_move_1, self.sensor_move_2], self.sensor_changed, ValueChangeEventFilter())

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

Documentation
^^^^^^^^^^^^^^^^^^

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
    from HABApp.core.events import ValueUpdateEventFilter
    from HABApp.util.multimode import MultiModeItem, ValueMode

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem
            item = MultiModeItem.get_create_item('MultiModeTestItem')
            item.listen_event(self.item_update, ValueUpdateEventFilter())

            # create two different modes which we will use and add them to the item
            auto = ValueMode('Automatic', initial_value=5)
            manu = ValueMode('Manual', initial_value=0)
            # Add the auto mode with priority 0 and the manual mode with priority 10
            item.add_mode(0, auto).add_mode(10, manu)

            # This shows how to enable/disable a mode and how to get a mode from the item
            print('disable/enable the higher priority mode')
            item.get_mode('manual').set_enabled(False)  # disable mode
            item.get_mode('manual').set_value(11)       # setting a value will enable it again

            # This shows that changes of the lower priority is only shown when
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
    from HABApp.core.events import ValueUpdateEventFilter
    from HABApp.util.multimode import MultiModeItem, ValueMode

    class MyMultiModeItemTestRule(HABApp.Rule):
        def __init__(self):
            super().__init__()

            # create a new MultiModeItem
            item = MultiModeItem.get_create_item('MultiModeTestItem')
            item.listen_event(self.item_update, ValueUpdateEventFilter())

            # helper to print the heading so we have a nice output
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
            # mode closes the shutter again. This could be achieved by automatically disabling the
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
The SwitchItemMode is same as ValueMode but enabled/disabled of the mode is controlled by a openHAB
:class:`~HABApp.openhab.items.SwitchItem`. This is very useful if the mode shall be deactivated from the openHAB sitemaps.

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
            # Now everything can be enabled/disabled from the openHAB sitemap
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
