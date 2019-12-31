import functools
import logging
import traceback

import HABApp

log = logging.getLogger('HABApp')


def log_exception(func):

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            lines = traceback.format_exc().splitlines()
            del lines[1:3]  # Remove entries which point to this wrapper

            # log exception, since it is unexpected we push it to stdout, too
            print(f'Error {e} in {func.__name__}:')
            log.error(f'Error {e} in {func.__name__}:')
            for line in lines:
                print(line)
                log.error(line)

            # send Error to internal event bus so we can reprocess it and notify the user
            HABApp.core.EventBus.post_event(
                'HABApp.Errors', HABApp.core.events.habapp_events.HABAppError(
                    func_name=func.__name__, exception=e, traceback='\n'.join(lines)
                )
            )

            # re raise exception, since this is something we didn't anticipate
            raise

    return f
