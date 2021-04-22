from string import Template
from .platform_defaults import get_log_folder, is_openhabian


def get_default_logfile() -> str:
    template = Template("""
${LOG_LEVELS}formatters:
  HABApp_format:
    format: '[%(asctime)s] [%(name)25s] %(levelname)8s | %(message)s'
${FRONTAIL_FORMAT}

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

    formatter: ${HABAPP_FILE_FORMAT}
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
    subs = {
        'EVENT_FILE': 'events.log',
        'HABAPP_FILE': 'HABApp.log',
        'HABAPP_FILE_FORMAT': 'HABApp_format',
        'FRONTAIL_FORMAT': '',
        'LOG_LEVELS': '',
    }

    # Use abs path and rename events.log if we log in the openhab folder
    log_folder = get_log_folder()
    if log_folder is not None:
        # Absolute so we can log errors if the config is faulty
        subs['HABAPP_FILE'] = (log_folder / subs['HABAPP_FILE']).as_posix()

        # Keep this relative so it is easier to read in the file
        subs['EVENT_FILE'] = 'HABApp_events.log'

        # With openhabian we typically use frontail
        if is_openhabian():
            subs['FRONTAIL_FORMAT'] = '\n'\
                '  Frontail_format:\n' \
                "    format: '%(asctime)s.%(msecs)03d [%(levelname)-5s] [%(name)-36s] - %(message)s'\n" \
                "    datefmt: '%Y-%m-%d %H:%M:%S'"

            subs['HABAPP_FILE_FORMAT'] = 'Frontail_format'

            # frontail expects WARN instead of WARNING
            subs['LOG_LEVELS'] = 'levels:\n  WARNING: WARN\n\n'

    return template.substitute(**subs)
