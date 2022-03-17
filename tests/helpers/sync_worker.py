import pytest

from HABApp.core.internals.wrapped_function import wrapped_sync


class SyncTestWorker:
    @staticmethod
    def submit(callback, *args, **kwargs):
        callback(*args, **kwargs)


@pytest.fixture(scope="function")
def sync_worker(monkeypatch):
    monkeypatch.setattr(wrapped_sync, 'WORKERS', SyncTestWorker())
    yield
