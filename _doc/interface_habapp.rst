######################################
HABApp
######################################

This page describes the HABApp internals


**************************************
Items
**************************************

Item
======================================
.. inheritance-diagram:: HABApp.core.items.Item
   :parts: 1

.. autoclass:: HABApp.core.items.Item
   :members:
   :inherited-members:
   :member-order: groupwise

ColorItem
======================================
.. inheritance-diagram:: HABApp.core.items.ColorItem
   :parts: 1

.. autoclass:: HABApp.core.items.ColorItem
   :members:
   :inherited-members:
   :member-order: groupwise

AggregationItem
======================================
The aggregation item is an item which takes the values of another item in a time period as an input.
It then allows to process these values and generate an aggregated output based on it.
The item makes implementing time logic like "Has it been dark for the last hour?" or
"Was there frost during the last six hours?" really easy.
And since it is just like a normal item triggering on changes etc. is possible, too.

.. execute_code::
    :hide_output:

    from HABApp.core.items import AggregationItem
    my_agg = AggregationItem.get_create_item('MyAggregationItem')

    # Connect the source item with the aggregation item
    my_agg.aggregation_source('MyInputItem')

    # Aggregate all changes in the last two hours
    my_agg.aggregation_period(2 * 3600)

    # Use max as an aggregation function
    my_agg.aggregation_func = max


The value of ``my_agg`` in the example will now always be the maximum of ``MyInputItem`` in the last two hours.
It will automatically update and always reflect the latest changes of ``MyInputItem``.



.. inheritance-diagram:: HABApp.core.items.AggregationItem
   :parts: 1

.. autoclass:: HABApp.core.items.AggregationItem
   :members:
   :inherited-members:
   :member-order: groupwise


BaseValueItem
======================================
Base class for items with values. All items that have a value must inherit from :class:`~HABApp.core.items.BaseValueItem`
May not be instantiated directly.

.. inheritance-diagram:: HABApp.core.items.BaseValueItem
   :parts: 1

.. autoclass:: HABApp.core.items.BaseValueItem
   :members:
   :inherited-members:
   :member-order: groupwise



**************************************
Events
**************************************

ValueUpdateEvent
======================================

This event gets emitted every time a value of an item receives an update

.. inheritance-diagram:: HABApp.core.events.ValueUpdateEvent
   :parts: 1

.. autoclass:: HABApp.core.events.ValueUpdateEvent
   :members:
   :inherited-members:


ValueChangeEvent
======================================

This event gets emitted every time a value of an item changes

.. inheritance-diagram:: HABApp.core.events.ValueChangeEvent
   :parts: 1

.. autoclass:: HABApp.core.events.ValueChangeEvent
   :members:
   :inherited-members:


ItemNoUpdateEvent
======================================

This event gets emitted when an item is watched for updates and no update has been made in a certain amount of time.

.. inheritance-diagram:: HABApp.core.events.ItemNoUpdateEvent
   :parts: 1

.. autoclass:: HABApp.core.events.ItemNoUpdateEvent
   :members:
   :inherited-members:


ItemNoChangeEvent
======================================

This event gets emitted when an item is watched for changes and no change has been made in a certain amount of time.

.. inheritance-diagram:: HABApp.core.events.ItemNoChangeEvent
   :parts: 1

.. autoclass:: HABApp.core.events.ItemNoChangeEvent
   :members:
   :inherited-members:
