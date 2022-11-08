**************************************
Troubleshooting
**************************************

Warnings
======================================

Starting of <FUNC_NAME> took too long.
--------------------------------------

This warning appears in the HABApp log, e.g.::

  Starting of MyRule.my_func took too long: 0.08s. Maybe there are not enough threads?

It means that the duration from when the event was received to the start of the execution of the function
took longer than expected.

This can be the case if suddenly many events are received at once.
Another reason for this warning might be that currently running function calls take too long to finish and thus no free
workers are available. This can either be the case for complex calculations,
but most of the time it's blocking function calls or a ``time.sleep`` call.

If these warnings pile up in the log it's an indicator that the worker is congested.
Make sure there is no use of long sleeps and instead the scheduler is used.

If this warning only appears now and then it can be ignored.


Execution of <FUNC_NAME> took too long
--------------------------------------

This warning appears in the HABApp log, e.g.::

  Execution of MyRule.my_long_func took too long: 15.25s

It means that the function took very long to execute. By default HABApp has 10 threads and each function call
will happen in one of those threads. Normally this is not a problem because functions finish rather quicly
and the used thread is free for the next function call.
When functions take very long to execute and multiple of these functions run parallel it's possible that
all threads are blocked. HABApp will then appear to "hang" and can not process new events.

If the function uses ``time.sleep`` it can be split up and the scheduler can be used instead.

Long running scripts (>10s) which do not interact with openHAB
can be run as a separate process with :meth:`~HABApp.Rule.execute_python`.
The script can e.g. print the result as a json which HABApp can read and load again into the proper data structures.


If this warning only appears now and then it can be ignored.


Errors
======================================

ValueError: Line is too long
--------------------------------------

The underlaying libraries of HABApp use a buffer to process each request and event from openHAB.
If the openHAB items contain images this buffer might be not enough and a ``ValueError: Line is too long``
error will appear in the logs. See :ref:`the openHAB connection options<CONFIG_OPENHAB_CONNECTION>` on how to increase
the buffer. The maximum image size that can be used without error is ~40% of the buffer size.
