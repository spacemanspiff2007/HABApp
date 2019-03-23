
def get_default_logfile() -> str:
    return """version : 1


formatters:
  HABApp_format:
    format: '[%(asctime)s] [%(name)25s] %(levelname)8s | %(message)s'


handlers:
  HABApp_default:
    class: logging.handlers.RotatingFileHandler
    filename: 'HABApp.log'
    maxBytes: 10_485_760
    backupCount: '3'

    formatter: HABApp_format
    level: DEBUG

  EventFile:
    class: logging.handlers.RotatingFileHandler
    filename: 'events.log'
    maxBytes: 10_485_760
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

  HABApp.Events:
    level: INFO
    handlers:
      - BufferEventFile
    propagate: False

"""
