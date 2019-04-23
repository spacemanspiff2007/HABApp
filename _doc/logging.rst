

Logging
==================================


Example usage
------------------------------
The logging library is the standard python library.

.. literalinclude:: ../conf/rules/logging_rule.py


Example configuration
------------------------------
Configuration of logging is done through `Logging.yml`. During the first start a configuration will be created.
It is recommended to extend the default configuration.

The complete description of the file format can be found `here <https://docs.python.org/3/library/logging.config.html?highlight=dictconfig#configuration-dictionary-schema>`_,
but the format should be pretty straight forward.

.. code-block:: yaml
    
    # required, can not be omitted but does nothing
    version : 1
    
    # describes the output format
    formatters:
      HABApp_format:
        format: '[%(asctime)s] [%(name)25s] %(levelname)8s | %(message)s'
    
    # describes the available file handlers
    handlers:
      HABApp_default:
        class: logging.handlers.RotatingFileHandler
        filename: 'HABApp.log'
        maxBytes: 10_000_000
        backupCount: '3'
    
        formatter: HABApp_format  # use the specified formater (see above)
        level: DEBUG
      
      MyRuleHandler:
        class: logging.handlers.RotatingFileHandler
        filename: 'MyRule.log'    # relative or absolute filenames can be used
        maxBytes: 10_000_000
        backupCount: '3'
    
        formatter: HABApp_format  # use the specified formater (see above)
        level: DEBUG
    
    
    # List all available loggers
    loggers:
      HABApp:
        level: DEBUG
        handlers:
          - HABApp_default  # This logger does log with the default handler
        propagate: False
    
      MyRule:
        level: DEBUG
        handlers:
          - MyRuleHandler  # This logger uses the MyRuleHandler
        propagate: False

    