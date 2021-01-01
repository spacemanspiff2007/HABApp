from string import Template
from .platform_defaults import get_log_folder


def get_default_logfile() -> str:
    template = Template("""
formatters:
  HABApp_format:
    format: '[%(asctime)s] [%(name)25s] %(levelname)8s | %(message)s'


handlers:
  # There are several Handlers available:
  #  - logging.handlers.RotatingFileHandler:
  #    Will rotate when the file reaches a certain size (see python logging documentation for args)
  #  - HABApp.core.lib.handler.MidnightRotatingFileHandler:
  #    Will wait until the file reaches a certain size and then rotate on midnight
  #  - More handlers:
  #    https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler

  HABApp_default:
    class: HABApp.core.lib.handler.MidnightRotatingFileHandler
    filename: '${HABAPP_FILE}'
    maxBytes: 1_048_576
    backupCount: 3

    formatter: HABApp_format
    level: DEBUG

  EventFile:
    class: HABApp.core.lib.handler.MidnightRotatingFileHandler
    filename: '${EVENT_FILE}'
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

""")

    # Default values are relative
    subs = {'EVENT_FILE': 'events.log', 'HABAPP_FILE': 'HABApp.log'}

    # Use abs path and rename events.log if we log in the openhab folder
    log_folder = get_log_folder()
    if log_folder is not None:
        # Absolute so we can log errors if the config is faulty
        subs['HABAPP_FILE'] = (log_folder / subs['HABAPP_FILE']).as_posix()

        # Keep this relative so it is easier to read in the file
        subs['EVENT_FILE'] = 'HABApp_events.log'

    return template.substitute(**subs)
