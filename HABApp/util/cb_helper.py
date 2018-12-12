import itertools
import logging
import traceback


class CallbackHelper:
    def __init__(self, name='', logger=None):
        self.__cb_funcs = []
        self.__cb_last = []

        if logger is None:
            logger = logging.getLogger('CallbackHelper')
        assert isinstance(logger, logging._loggerClass)
        self.__log = logger

        if not name:
            name = self.__class__.__name__
        self.__name = name

        self.requested = False

    def register_func(self, func, last=False):
        assert callable(func)
        if last:
            self.__cb_last.append(func)
        else:
            self.__cb_funcs.append(func)

    def request(self):
        "Request execution of all functions"
        self.__log.debug(f'{self.__name} started')

        self.requested = True

        for func in itertools.chain(self.__cb_funcs, self.__cb_last):
            try:
                self.__log.debug(f'Calling {func.__name__}')
                func()
                self.__log.debug(f'{func.__name__} done!')
            except Exception as ex:
                self.__log.error(ex)
                tb = traceback.format_exc().splitlines()
                for line in tb:
                    self.__log.error(line)

        self.__log.debug(f'{self.__name} finished')
        return None
