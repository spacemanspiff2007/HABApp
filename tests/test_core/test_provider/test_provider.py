from collections.abc import AsyncGenerator, Generator
from types import TracebackType
from typing import Any

from HABApp.core.provider import HabAppObjProvider


async def test_provider_simple_call() -> None:
    calls = []
    p = HabAppObjProvider()

    @p.register
    def p1() -> int:
        calls.append('p1')
        return 0

    @p.register
    def p2() -> dict:
        calls.append('p2')
        return {}

    @p.register
    def a(x: int) -> str:
        calls.append(f'a({x})')
        return 'asdf'

    @p.register
    def b(x: int, y: dict) -> tuple:
        calls.append(f'b({x}, {y})')
        return ('asdf', )

    assert await p.get(str) == 'asdf'
    assert calls == ['p1', 'a(0)']

    calls.clear()
    assert await p.get(tuple) == ('asdf', )
    assert calls == ['p1', 'p2', 'b(0, {})']


async def test_provider_simple_call_cleanup() -> None:
    calls = []
    p = HabAppObjProvider()

    @p.register
    def p1() -> Generator[int, None, None]:
        calls.append('p1')
        yield 0
        calls.append('p1 close')

    @p.register
    def p2(key: int) -> Generator[dict[int, int], None, None]:
        calls.append('p2')
        yield {key: 10}
        calls.append('p2 close')

    @p.register
    def p3() -> Generator[str, None, None]:
        calls.append('p3')
        yield 'asdf'
        calls.append('p3 close')

    @p.register
    def a(x: str, y: dict[int, int]) -> Generator[tuple, None, None]:
        calls.append(f'a({x}, {y})')
        yield ('asdf', )
        calls.append('a close')

    assert await p.get(tuple) == ('asdf', )
    assert calls == ['p3', 'p1', 'p2', 'a(asdf, {0: 10})']

    calls.clear()
    await p.close()

    assert calls == ['a close', 'p2 close', 'p1 close', 'p3 close']


def test_has_factory() -> None:
    def func() -> list:
        pass

    p = HabAppObjProvider()
    p.register(func)
    assert p.has_factory(list)
    # noinspection PyTypeChecker
    assert not p.has_factory([])


async def test_type_factory_callable() -> None:
    def func() -> int:
        return 1

    p = HabAppObjProvider()
    p.register(func)
    assert await p.get(int) == 1


async def test_type_factory_class() -> None:
    class MyCls:
        pass

    p = HabAppObjProvider()
    p.register(MyCls)
    assert isinstance(await p.get(MyCls), MyCls)


async def test_type_factory_coroutine() -> None:
    async def func() -> int:
        return 1

    p = HabAppObjProvider()
    p.register(func)
    assert await p.get(int) == 1


async def test_type_factory_sync_generator() -> None:
    calls = []

    def func() -> Generator[int, Any, None]:
        yield 1
        calls.append('close')

    p = HabAppObjProvider()
    p.register(func)
    assert await p.get(int) == 1
    await p.close()

    assert calls == ['close']


async def test_type_factory_async_generator() -> None:
    calls = []

    async def func() -> AsyncGenerator[int, Any]:
        yield 1
        calls.append('close')

    p = HabAppObjProvider()
    p.register(func)
    assert await p.get(int) == 1
    await p.close()

    assert calls == ['close']


async def test_type_factory_class_sync_context_manager() -> None:
    calls = []

    class MyCls:
        def __enter__(self):
            calls.append('enter')
            return self

        def __exit__(self, exc_type: type[BaseException] | None,
                     exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
            calls.append('exit')

    p = HabAppObjProvider()
    p.register(MyCls)
    assert isinstance(await p.get(MyCls), MyCls)
    await p.close()

    assert calls == ['enter', 'exit']


async def test_type_factory_class_async_context_manager() -> None:
    calls = []

    class MyCls:
        async def __aenter__(self):
            calls.append('enter')
            return self

        async def __aexit__(self, exc_type: type[BaseException] | None,
                            exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
            calls.append('exit')

    p = HabAppObjProvider()
    p.register(MyCls)
    assert isinstance(await p.get(MyCls), MyCls)
    await p.close()

    assert calls == ['enter', 'exit']


async def test_multiple_enter() -> None:
    def func() -> Generator[list, Any, None]:
        obj = []
        calls.append(('yield', id(obj)))
        yield obj
        calls.append(('close', id(obj)))

    calls = []
    p = HabAppObjProvider()
    p.register(func)

    target = []

    async with p:
        obj = await p.get(list)
        target.append(('yield', id(obj)))
        target.append(('close', id(obj)))

    async with p:
        obj = await p.get(list)
        target.append(('yield', id(obj)))
        target.append(('close', id(obj)))

    assert calls == target


p = HabAppObjProvider()


class SomeClass:
    @p.register
    @classmethod
    def create(cls) -> 'SomeClass':
        return SomeClass()


async def test_deferred() -> None:
    assert p._deferred
    assert isinstance(await p.get(SomeClass), SomeClass)
    assert not p._deferred
