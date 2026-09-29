import asyncio
from collections.abc import AsyncGenerator, Generator
from types import TracebackType
from typing import Any

import pytest

from HABApp.core.provider import HabAppObjProvider
from HABApp.core.provider.provider import CyclicDependencyError, FactoryNotFoundError


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
    assert calls == ['p2', 'b(0, {})']


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


async def test_create_once() -> None:

    p = HabAppObjProvider()

    @p.register
    def func() -> list:
        return []

    @p.register
    def func2(l: list) -> dict:
        return {'l': l}

    l1 = await p.get(list)
    l2 = await p.get(list)
    assert l1 is l2

    d1 = await p.get(dict)
    d2 = await p.get(dict)

    assert d1['l'] is l1
    assert d2['l'] is l1


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


async def test_type_factory_class_with_params() -> None:
    p = HabAppObjProvider()

    @p.register
    class MyCls:
        def __init__(self, p: int) -> None:
            self.p = p

    @p.register
    def func() -> int:
        return 1

    obj = await p.get(MyCls)
    assert isinstance(obj, MyCls)
    assert obj.p == 1


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


async def test_cyclic_dependency() -> None:

    def func_int(obj: str | None) -> int:
        pass

    def func_bool(obj: int) -> bool:
        pass

    def func_str(obj: bool) -> str | None:
        pass

    p = HabAppObjProvider()
    p.register(func_int)
    p.register(func_bool)
    p.register(func_str)

    with pytest.raises(CyclicDependencyError) as e:
        await p.get(int)
    assert str(e.value) == 'Cyclic dependency: int -> bool -> str | None -> int'


async def test_create_all() -> None:
    calls = []

    def func_int() -> int:
        calls.append('int')
        return 0

    def func_bool(obj: int) -> bool:
        calls.append('bool')
        return True

    def func_str(obj: bool) -> str:
        calls.append('str')
        return 'a'

    def func_list() -> list:
        calls.append('list')
        return []

    def func_dict(a: list, b: str) -> dict:
        calls.append('dict')
        return {}

    p = HabAppObjProvider()
    p.register(func_int)
    p.register(func_list)
    p.register(func_bool)
    p.register(func_str)
    p.register(func_dict)

    await p.create_all()

    assert calls == ['int', 'list', 'bool', 'str', 'dict']


async def test_create_all_error() -> None:

    def func_int() -> int:
        pass

    def func_bool(obj: int) -> bool:
        pass

    def func_dict(a: list, b: int) -> dict:
        pass

    p = HabAppObjProvider()
    p.register(func_int)
    p.register(func_bool)
    p.register(func_dict)

    with pytest.raises(FactoryNotFoundError) as e:
        await p.create_all()
    assert str(e.value) == "No factory registered for type <class 'list'>"


async def test_concurrent_create() -> None:

    event = asyncio.Event()

    async def factory_with_delay() -> AsyncGenerator[dict, Any]:
        await event.wait()
        yield {}

    p = HabAppObjProvider()
    p.register(factory_with_delay)

    async def request_object():
        return await p.get(dict)

    tasks = [asyncio.create_task(request_object()) for _ in range(50)]

    await asyncio.sleep(0.1)
    event.set()

    obj = await p.get(dict)

    # All should return the same object
    results = await asyncio.gather(*tasks)
    assert {id(r) for r in results} == {id(obj) for _ in results}
