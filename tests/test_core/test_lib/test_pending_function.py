import asyncio

import pytest
from whenever import Instant, TimeDelta

from HABApp.core.lib import DebouncedCall, DebouncedCallRegistry
from HABApp.core.lib.asyncio.asyncio import AsyncioProvider


async def dummy_coro() -> None:
    pass


@pytest.fixture
async def registry() -> DebouncedCallRegistry:
    r = DebouncedCallRegistry(AsyncioProvider())
    yield r
    await r.shutdown()


class DummyCoro:
    def __init__(self) -> None:
        self._calls = []

    async def __call__(self) -> None:
        self._calls.append(Instant.now())

    @property
    def called(self) -> int:
        return len(self._calls)


@pytest.fixture
async def cb() -> DummyCoro:
    return DummyCoro()


class TestDebouncedCall:

    async def test_init(self, registry: DebouncedCallRegistry) -> None:
        with pytest.raises(TypeError):
            DebouncedCall(lambda: None, 1.0, registry=registry)  # type: ignore[arg-type]

        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            DebouncedCall(dummy_coro, -1, registry=registry)
        assert str(exc_info.value) == 'Timeout must be a >= 0! Is: -PT1S'

        with pytest.raises(TypeError):
            DebouncedCall(dummy_coro, '5', registry=registry)  # type: ignore[arg-type]

        p = DebouncedCall(dummy_coro, TimeDelta(seconds=2.5), registry=registry)
        assert p._timeout == TimeDelta(seconds=2.5)

        p = DebouncedCall(dummy_coro, TimeDelta.ZERO, registry=registry)
        assert p._timeout == TimeDelta.ZERO

        p = DebouncedCall(dummy_coro, 1.0, registry=registry)
        assert p._task is None

    async def test_repr(self, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(dummy_coro, 1.5, registry=registry)
        assert repr(p) == '<DebouncedCall func=dummy_coro timeout=PT1.5S running=False>'

        p = DebouncedCall(dummy_coro, 1.0, registry=registry)
        p.reset()
        assert repr(p) == '<DebouncedCall func=dummy_coro timeout=PT1S running=True>'

    async def test_func_called_after_timeout(self, cb: DummyCoro, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(cb, 0.02, registry=registry)
        p.reset()
        assert cb.called == 0
        await asyncio.sleep(0.1)
        assert cb.called == 1

    async def test_reset_debounces_multiple_calls(self, cb: DummyCoro, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(cb, 0.05, registry=registry)
        for _ in range(7):
            p.reset()
            await asyncio.sleep(0.01)

        assert cb.called == 0
        await asyncio.sleep(0.1)
        assert cb.called == 1

    async def test_sequential_resets_each_trigger_func(self, cb: DummyCoro, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(cb, 0.02, registry=registry)
        for _ in range(3):
            p.reset()
            await asyncio.sleep(0.05)

        assert cb.called == 3

    async def test_cancel_prevents_execution(self, cb: DummyCoro, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(cb, 0.02, registry=registry)
        p.reset()
        p.cancel()
        await asyncio.sleep(0.1)
        assert cb.called == 0

    async def test_double_cancel_is_safe(self, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(dummy_coro, 0.1, registry=registry)
        p.reset()
        p.cancel()
        p.cancel()
        assert p._task is None

    async def test_task_exists_while_pending(self, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(dummy_coro, 1.0, registry=registry)
        p.reset()
        assert p._task is not None
        p.cancel()

    async def test_task_is_none_after_cancel(self, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(dummy_coro, 1.0, registry=registry)
        p.reset()
        p.cancel()
        await asyncio.sleep(0.01)
        assert p._task is None

    async def test_task_is_none_after_completion(self, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(dummy_coro, 0.01, registry=registry)
        p.reset()
        await asyncio.sleep(0.05)
        assert p._task is None


class TestDebouncedCallRegistry:

    async def test_register_obj(self, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(dummy_coro, 0.1, registry=registry)

        registry.register_obj(p)
        registry.register_obj(p)    # doesn't register again

        assert p in registry
        assert registry._objs.count(p) == 1

        registry.remove_obj(p)
        registry.remove_obj(p)  # must not raise

        assert p not in registry

    async def test_disabled_prevents_task_creation(self, cb: DummyCoro, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(cb, 0.001, registry=registry)
        registry.enabled = False
        p.reset()
        await asyncio.sleep(0.05)
        assert cb.called == 0
        assert p._task is None

    async def test_shutdown_cancels_pending(self, cb: DummyCoro, registry: DebouncedCallRegistry) -> None:
        p = DebouncedCall(cb, 0.05, registry=registry)
        p.reset()
        await registry.shutdown()
        await asyncio.sleep(0.1)
        assert cb.called == 0

    async def test_shutdown_sets_enabled_false(self, registry: DebouncedCallRegistry) -> None:
        await registry.shutdown()
        assert registry.enabled is False

    async def test_sleep_negative(self, registry: DebouncedCallRegistry) -> None:
        past = Instant.now().subtract(hours=1)
        # Should complete without hanging even though target is in the past
        await asyncio.wait_for(registry.asyncio.sleep(past), timeout=0.1)

    async def test_repr(self, registry: DebouncedCallRegistry) -> None:
        assert repr(registry) == '<DebouncedCallRegistry objs=0>'
