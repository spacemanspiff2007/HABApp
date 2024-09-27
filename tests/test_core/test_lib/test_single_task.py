import asyncio
from unittest.mock import Mock

from HABApp.core.lib import SingleTask


async def test_single_task_start() -> None:

    m = Mock()

    async def cb() -> None:
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
