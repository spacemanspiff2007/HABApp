import logging

from HABApp.config.logging import get_logging_dict
from HABApp.config.logging.config import remove_memory_handler_from_cfg, inject_queue_handler

log = logging.getLogger('test')


def test_add_version(test_logs):
    assert get_logging_dict({}, log)[0] == {'version': 1}


def get_unpack(log_dict):
    value = get_logging_dict(log_dict, log)[0]
    value.pop('version')
    return value


def test_fix_old_logger(test_logs):
    cfg = {'handlers': {'my_handler': {'class': 'HABApp.core.lib.handler.MidnightRotatingFileHandler'}}}
    dst = {'handlers': {'my_handler': {'class': 'HABApp.config.logging.MidnightRotatingFileHandler'}}}
    test_logs.add_expected(
        'test', logging.WARNING,
        'Replaced class for handler "my_handler" with HABApp.config.logging.MidnightRotatingFileHandler'
    )

    assert get_unpack(cfg) == dst


def test_remove_memory_handler(test_logs):
    cfg = {
        'handlers': {
            'BufferEventFile': {'class': 'logging.handlers.MemoryHandler', 'target': 'EventFile'},
            'EventFile': {'class': 'logging.handlers.RotatingFileHandler', 'filename': 'events.log'},
        },
        'loggers': {
            'HABApp.EventBus': {'handlers': ['BufferEventFile'], 'level': 'DEBUG', 'propagate': False}
        }
    }

    dst = {
        'handlers': {
            'EventFile': {'class': 'logging.handlers.RotatingFileHandler', 'filename': 'events.log'},
        },
        'loggers': {
            'HABApp.EventBus': {'handlers': ['EventFile'], 'level': 'DEBUG', 'propagate': False}
        }
    }

    remove_memory_handler_from_cfg(cfg['handlers'], cfg['loggers'], log)
    assert cfg == dst

    test_logs.add_expected(
        'test', logging.ERROR,
        '"logging.handlers.MemoryHandler" is no longer required. Please remove from config (BufferEventFile)!'
    )
    test_logs.add_expected('test', logging.WARNING, 'Removed BufferEventFile from handlers')
    test_logs.add_expected('test', logging.WARNING, 'Replaced BufferEventFile with EventFile for logger HABApp.EventBus')


def test_inject_queue_handler():
    cfg = {
        'handlers': {
            'EventFile': {'class': 'logging.handlers.RotatingFileHandler', 'filename': 'events.log'},
        },
        'loggers': {
            'HABApp.EventBus': {'handlers': ['BufferEventFile'], 'level': 'DEBUG', 'propagate': False}
        }
    }

    handlers = inject_queue_handler(cfg['handlers'], cfg['loggers'], log)

    dst = {
        'handlers': {
            'EventFile': {'class': 'logging.handlers.RotatingFileHandler', 'filename': 'events.log'},
            'HABAppQueue_BufferEventFile': {'class': 'logging.handlers.QueueHandler', 'queue': handlers[0]._queue},
        },
        'loggers': {
            'HABApp.EventBus': {'handlers': ['HABAppQueue_BufferEventFile'], 'level': 'DEBUG', 'propagate': False}
        }
    }

    assert cfg == dst
