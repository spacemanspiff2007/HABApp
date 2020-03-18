
Advanced Usage
==================================

HABApp Topics
------------------------------
There are several internal topics which can be used to react to HABApp changes from within rules.
An example would be dynamically reloading rules when a parameter file gets reloaded
(e.g. when :class:`~HABApp.parameters.Parameter` is used to create rules dynamically) or
an own notifier in case there are errors (e.g. Pushover).

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Topic
     - Description
     - Events

   * - HABApp.Rules
     - The corresponding events trigger a load/unload of the rule file specified in the event
     - :class:`~HABApp.core.events.habapp_events.RequestFileLoadEvent` and :class:`~HABApp.core.events.habapp_events.RequestFileUnloadEvent`

   * - HABApp.Parameters
     - The corresponding events trigger a load/unload of the parameter file specified in the event
     - :class:`~HABApp.core.events.habapp_events.RequestFileLoadEvent` and :class:`~HABApp.core.events.habapp_events.RequestFileUnloadEvent`

   * - HABApp.Errors
     - All errors in functions and rules of HABApp create an according event. Use this topic to create an own notifier
       in case of errors (e.g. Pushover).
     - :class:`~HABApp.core.events.file_events.HABAppError`



.. autoclass:: HABApp.core.events.habapp_events.RequestFileLoadEvent
   :members:

.. autoclass:: HABApp.core.events.habapp_events.RequestFileUnloadEvent
   :members:

.. autoclass:: HABApp.core.events.habapp_events.HABAppError
   :members:

AggregationItem
------------------------------
The aggregation item which takes another item as an input. It then allows to aggregate the state changes
and generate an output based on it.
The item makes implementing time logic like "Has it been dark for the last hour?" or
"Was there frost during the last six hours?" really easy.
And since it is just like a normal item triggering on changes is possible, too.

.. execute_code::
    :hide_output:

    from HABApp.core.items import AggregationItem
    my_agg = AggregationItem('MyAggregationItem')

    # Connect the source item with the aggregation item
    my_agg.aggregation_source('MyInputItem')

    # Aggregate all changes in the last hour
    my_agg.aggregation_period(3600)

    # Use max as an aggregation function
    my_agg.aggregation_func = max

The value of ``my_add`` in the example will now always be the maximum of ``MyInputItem`` in the last two hours.
It will automatically update and always reflect the latest changes of ``MyInputItem``.


.. autoclass:: HABApp.core.items.AggregationItem
   :members: