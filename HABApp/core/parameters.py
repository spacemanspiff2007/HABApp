import logging
import pathlib
import typing

from watchdog.observers import Observer

from HABApp.util import CallbackHelper, SimpleFileWatcher

log = logging.getLogger('HABApp.Parameters')


class RuntimeParameters:
    def __init__(self):
        self._params:typing.Dict[str,typing.Dict] = None
        self.__folder_watcher : Observer = None
        
    def get_parameter(self, filename, *parameters):
        assert parameters, parameters
        
        try:
            file_content = self._params[filename]
        except KeyError:
            raise FileNotFoundError(f'File {filename:s}.yml not found')

        ret = file_content
        for p in parameters:
            ret = ret[p]
        return ret
    
    def setup(self, path: pathlib.Path, shutdown_helper: CallbackHelper):
        # folder watcher
        self.__folder_watcher = Observer()
        self.__folder_watcher.schedule(
            SimpleFileWatcher(self.param_changed, file_ending='.yml'), str(path)
        )
        self.__folder_watcher.start()

        # proper shutdown
        shutdown_helper.register_func(self.__folder_watcher.stop)
        shutdown_helper.register_func(self.__folder_watcher.join, last=True)
        
    def param_changed(self, path):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("{}\n{}".format( e, traceback.format_exc()))
            raise
    