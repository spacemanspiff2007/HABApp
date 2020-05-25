
def get_default_logfile() -> str:
    return """version : 1


formatters:
  HABApp_format:
    format: '[%(asctime)s] [%(name)25s] %(levelname)8s | %(message)s'


handlers:
  # There are several Handlers available:
  # logging.handlers.RotatingFileHandler:
  #   Will rotate when the file reaches a certain size (see python logging documentation for args)
  # HABApp.core.lib.handler.MidnightRotatingFileHandler:
  #   Will wait until the file reaches a certain size and then rotate on midnight
  # More handlers:
  # https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler

  HABApp_default:
    class: HABApp.core.lib.handler.MidnightRotatingFileHandler
    filename: 'HABApp.log'
    maxBytes: 1_048_576
    backupCount: 3

    formatter: HABApp_format
    level: DEBUG

  EventFile:
    class: HABApp.core.lib.handler.MidnightRotatingFileHandler
    filename: 'events.log'
    maxBytes: 1_048_576
    backupCount: 3

    formatter: HABApp_format
    level: DEBUG

  BufferEventFile:
    class: logging.handlers.MemoryHandler
    capacity: 10
    formatter: HABApp_format
    target: EventFile
    level: DEBUG


loggers:
  HABApp:
    level: INFO
    handlers:
      - HABApp_default
    propagate: False

  HABApp.EventBus:
    level: INFO
    handlers:
      - BufferEventFile
    propagate: False

"""
