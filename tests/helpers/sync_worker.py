import pytest

from HABApp.core.internals.wrapped_function import wrapped_thread


class SyncTestWorker:
    @staticmethod
    def submit(callback, *args, **kwargs):
        callback(*args, **kwargs)


@pytest.fixture(scope="function")
def sync_worker(monkeypatch):
    monkeypatch.setattr(wrapped_thread, 'WORKERS', SyncTestWorker())
    yield
