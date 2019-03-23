import itertools
import logging
import traceback


class ShutdownHelper:
    def __init__(self, name=''):
        self.__cb_funcs = []
        self.__cb_last = []

        self.requested = False

    def register_func(self, func, last=False):
        assert callable(func)
        if last:
            self.__cb_last.append(func)
        else:
            self.__cb_funcs.append(func)

    def request_shutdown(self):
        "Request execution of all functions"

        log = logging.getLogger('HABApp.Shutdown')
        log.debug('Requested shutdown')

        self.requested = True

        for func in itertools.chain(self.__cb_funcs, self.__cb_last):
            try:
                log.debug(f'Calling {func.__name__}')
                func()
                log.debug(f'{func.__name__} done!')
            except Exception as ex:
                log.error(ex)
                tb = traceback.format_exc().splitlines()
                for line in tb:
                    log.error(line)

        log.debug('Shutdown complete')
        return None
