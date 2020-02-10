import typing

from HABApp.core import EventBus, EventBusListener
from HABApp.core import WrappedFunction


class SyncWorker:
    def __init__(self):
        self.worker = WrappedFunction._WORKERS
        WrappedFunction._WORKERS = self

        self.listener: typing.List[EventBusListener] = []

    def listen_events(self, name: str, cb):
        listener = EventBusListener(name, WrappedFunction(cb, name=f'TestFunc for name'))
        self.listener.append(listener)
        EventBus.add_listener(listener)

    def submit(self, callback, *args, **kwargs):
        # submit never raises and exception, so we don't do it here, too
        try:
            callback(*args, **kwargs)
        except Exception as e:  # noqa: F841
            pass

    def remove(self):
        WrappedFunction._WORKERS = self.worker
        self.worker = None
        for l in self.listener:
            l.cancel()

    def __enter__(self):
        assert self.worker is not None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()

        # do not supress exception
        return False
