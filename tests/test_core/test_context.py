import pytest

from HABApp.core.asyncio import AsyncContextError, thread_context


async def test_error_msg() -> None:

    def my_sync_func():
        if thread_context.get(None) is None:
            raise AsyncContextError(my_sync_func)

    with pytest.raises(AsyncContextError) as e:
        my_sync_func()
    assert str(e.value) == 'Function "my_sync_func" may not be called from an async context!'

    thread_context.set('Test')
    my_sync_func()
