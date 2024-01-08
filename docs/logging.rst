
**************************************
Logging
**************************************

Configuration
======================================
Configuration of logging is done through the ``logging.yml``.
During the first start a default configuration will be created.
It is recommended to extend the default configuration.

The complete description of the file format can be found `here <https://docs.python.org/3/library/logging.config.html?highlight=dictconfig#configuration-dictionary-schema>`_,
but the format should be pretty straight forward.

.. hint::
   | It is highly recommended to use an absolute path as a file name, at least for the ``HABApp.log``
   | That way even if the HABApp configuration is invalid HABApp can still log the errors that have occurred.
   | e.g.: ``/HABApp/logs/habapp.log`` or ``c:\HABApp\logs\habapp.log``

Provided loggers
======================================

The ``HABApp.config.logging`` module provides additional loggers which can be used


.. autoclass:: HABApp.config.logging.MidnightRotatingFileHandler

.. autoclass:: HABApp.config.logging.CompressedMidnightRotatingFileHandler


Example
======================================

Usage
--------------------------------------
The logging library is the standard python library and an extensive description can be found
`in the official documentation <https://docs.python.org/3/library/logging.html>`_.

.. literalinclude:: ../run/conf/rules/logging_rule.py


To make the logging output work properly an output file and an output format has to be configured for the logger.
The logging library supports a logging hierarchy so the configuration for the logger ``MyRule`` will also work
logger ``MyRule.SubLogger`` and ``MyRule.SubLogger.SubSubLogger``.

The output of our logger from the example shall be in a separate file so we add a new output file
to the file configuration under ``handlers`` in the ``logging.yml``.

.. code-block:: yaml
   :emphasize-lines: 4-11

    handlers:
      ...

      MyRuleHandler: # <-- This is the name of the handler
        class: HABApp.config.logging.MidnightRotatingFileHandler
        filename: 'c:\HABApp\Logs\MyRule.log'
        maxBytes: 10_000_000
        backupCount: 3

        formatter: HABApp_format  # use this format
        level: DEBUG

The output file is now available for logging but the configuration for the logger is still missing.
It has to be added under ``loggers`` and reference the handler we created

.. code-block:: yaml
   :emphasize-lines: 4-8

    loggers:
      ...

      MyRule:              # <-- Name of the logger
        level: DEBUG       # <-- minimum Logging level, e.g. use INFO if you don't want the output of log.debug()
        handlers:
          - MyRuleHandler  # This logger uses the MyRuleHandler
        propagate: False

Now the logger works as expected and writes all output to the new file.

Full Example configuration
--------------------------------------

.. code-block:: yaml

    # -----------------------------------------------------------------------------------
    # Configuration of the available output formats
    # -----------------------------------------------------------------------------------
    formatters:
      HABApp_format:
        format: '[%(asctime)s] [%(name)25s] %(levelname)8s | %(message)s'

    # -----------------------------------------------------------------------------------
    # Configuration of the available file handlers (output files)
    # -----------------------------------------------------------------------------------
    handlers:
      HABApp_default:
        class: HABApp.config.logging.MidnightRotatingFileHandler
        filename: 'HABApp.log'
        maxBytes: 10_000_000
        backupCount: 3

        formatter: HABApp_format  # use the specified formatter (see above)
        level: DEBUG

      MyRuleHandler:
        class: HABApp.config.logging.MidnightRotatingFileHandler
        filename: 'c:\HABApp\Logs\MyRule.log'    # absolute filename is recommended
        maxBytes: 10_000_000
        backupCount: 3

        formatter: HABApp_format  # use the specified formatter (see above)
        level: DEBUG


    # -----------------------------------------------------------------------------------
    # Configuration of all available loggers and their configuration
    # -----------------------------------------------------------------------------------
    loggers:
      HABApp:
        level: DEBUG
        handlers:
          - HABApp_default  # This logger does log with the default handler
        propagate: False

      MyRule:   # <-- Name of the logger
        level: DEBUG
        handlers:
          - MyRuleHandler  # This logger uses the MyRuleHandler
        propagate: False


Custom log levels
======================================
It is possible to add custom log levels or rename existing levels.
This is possible via the optional ``levels`` entry in the logging configuration file.

.. code-block:: yaml

    levels:
      WARNING: WARN  # Changes WARNING to WARN
      5: TRACE       # Adds a new loglevel "TRACE" with value 5

    formatters:
      HABApp_format:
    ...


Logging to stdout
======================================

The following handler writes to stdout

.. code-block:: yaml

    handlers:
      StdOutHandler:
        class: logging.StreamHandler
        stream: ext://sys.stdout

        formatter: HABApp_format
        level: DEBUG


Add custom filters to loggers
======================================

It's possible to filter out certain parts of log files with a
`filter <https://docs.python.org/3/library/logging.html?highlight=logging%20filter#logging.Filter>`_.
The recommendation is to create the filter :ref:`during startup<ref_run_code_on_startup>`.

This example ignores all messages for the ``HABApp.EventBus`` logger that contain ``MyIgnoredString``.


.. exec_code::
   :hide_output:

   import logging

   # False to skip, True to log record
   def filter(record: logging.LogRecord) -> bool:
       return 'MyIgnoredString' not in record.msg


   logging.getLogger('HABApp.EventBus').addFilter(filter)

.. note::
   | Regular expressions for a filter should be compiled outside of the filter function with ``re.compile``
     for performance reasons.
   | A simple subtext search however will always have way better performance.
