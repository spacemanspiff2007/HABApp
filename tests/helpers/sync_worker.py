import pytest

from HABApp.core.internals.wrapped_function import wrapped_thread
from HABApp.core.internals.wrapped_function import wrapper as wrapper_module


class SyncTestWorker:
    @staticmethod
    def submit(callback, *args, **kwargs) -> None:
        callback(*args, **kwargs)


@pytest.fixture()
def sync_worker(monkeypatch) -> None:
    monkeypatch.setattr(wrapped_thread, 'POOL', SyncTestWorker())

    assert not hasattr(wrapper_module, 'SYNC_CLS')
    monkeypatch.setattr(wrapper_module, 'SYNC_CLS', wrapper_module.WrappedThreadFunction, raising=False)
