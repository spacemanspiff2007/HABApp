import pytest

from HABApp.core import WrappedFunction


class SyncTestWorker:
    def submit(self, callback, *args, **kwargs):
        callback(*args, **kwargs)


@pytest.fixture(scope="function")
def sync_worker(monkeypatch):
    monkeypatch.setattr(WrappedFunction, '_WORKERS', SyncTestWorker())
