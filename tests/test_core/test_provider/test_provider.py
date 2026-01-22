from collections.abc import Generator

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
    assert calls == ['p1', 'p2', 'b(0, None)']


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
