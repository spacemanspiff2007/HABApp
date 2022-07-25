import asyncio

from HABApp.core.lib import SingleTask
from unittest.mock import Mock


async def test_single_task_start():

    m = Mock()

    async def cb():
        m()

    st = SingleTask(cb)

    for _ in range(10):
        st.start()

    await asyncio.sleep(0.05)
    m.assert_called_once_with()
    assert st.task is None

    m.reset_mock()

    for _ in range(10):
        st.start()
        st.cancel()

    st.start()

    await asyncio.sleep(0.05)
    m.assert_called_once_with()
    assert st.task is None
