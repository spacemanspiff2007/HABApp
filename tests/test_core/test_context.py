import pytest

from HABApp.core.context import async_context, AsyncContextError


@pytest.mark.asyncio
async def test_error_msg():

    def my_sync_func():
        if async_context.get(None) is not None:
            raise AsyncContextError(my_sync_func)

    async_context.set('Test')
    with pytest.raises(AsyncContextError) as e:
        my_sync_func()
    assert str(e.value) == 'Function "my_sync_func" may not be called from an async context!'
