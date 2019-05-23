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

PrioritizedValue
------------------------------

Example
^^^^^^^^^^^^^^^^^^
.. execute_code::

    # hide
    from HABApp.util import PrioritizedValue
    # hide

    def print_value(val):
        print( f'   Output is {val}')

    p = PrioritizedValue(on_change=print_value)
    prio5 = p.get_value_changer(priority=5, initial_value=5)
    prio4 = p.get_value_changer(priority=4, initial_value=7)

    # values can be enabled/disabled
    print('set_enabled:')
    prio5.set_enabled(False)
    prio5.set_enabled(True)

    # Values can be set and will be change automatically according to priority
    print('set_value:')
    prio4.set_value(20)
    prio5.set_value(10)



Documentation
^^^^^^^^^^^^^^^^^^
.. autoclass:: PrioritizedValue
   :members:

.. autoclass:: HABApp.util.prioritized_value.ValueChanger()
   :members:

