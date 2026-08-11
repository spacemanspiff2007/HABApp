import pytest

from HABApp.core.errors import ContextNotSetError
from HABApp.core.internals import get_current_context
from HABApp.rule import Rule
from tests import SimpleRuleRunner


class OtherRule(Rule):
    def check_ctx(self) -> None:
        assert get_current_context() is self._habapp_ctx
        assert self._habapp_ctx is not None

    async def check_ctx_async(self) -> None:
        assert get_current_context() is self._habapp_ctx
        assert self._habapp_ctx is not None


@pytest.mark.no_internals
async def test_context_before_init() -> None:

    class BeforeInit(Rule):
        def __init__(self) -> None:
            self.func()
            super().__init__()

        def func(self) -> None:
            with pytest.raises(ContextNotSetError) as e:
                get_current_context()
            assert str(e.value) == (
                'Context is not set! When overriding __init__ make sure to call super().__init__() first.'
            )

    async with SimpleRuleRunner():
        BeforeInit()


@pytest.mark.no_internals
async def test_context_after_init() -> None:

    class BeforeAfterInit(OtherRule):
        def __init__(self) -> None:
            super().__init__()
            self.check_ctx()

    async with SimpleRuleRunner():
        r = BeforeAfterInit()
        r.check_ctx()


@pytest.mark.no_internals
async def test_context_before_init_other() -> None:

    async with SimpleRuleRunner():
        o = OtherRule()

        class BeforeInit(OtherRule):
            def __init__(self) -> None:
                self.check_ctx()
                super().__init__()

            def check_ctx(self) -> None:
                o.check_ctx()

                with pytest.raises(ContextNotSetError) as e:
                    super().check_ctx()
                assert str(e.value) == (
                    'Context is not set! When overriding __init__ make sure to call super().__init__() first.'
                )

        BeforeInit()


@pytest.mark.no_internals
async def test_context_after_init_other() -> None:

    async with SimpleRuleRunner():
        o = OtherRule()

        class AfterInit(OtherRule):
            def __init__(self) -> None:
                super().__init__()
                self.check_ctx()

            def check_ctx(self) -> None:
                o.check_ctx()
                super().check_ctx()

        AfterInit()


@pytest.mark.no_internals
async def test_context_a_b() -> None:

    async with SimpleRuleRunner():
        o = OtherRule()

        class MyRule(OtherRule):
            def test(self) -> None:
                self.check_ctx()
                o.check_ctx()

        MyRule().test()


@pytest.mark.no_internals
async def test_context_async() -> None:
    async with SimpleRuleRunner():
        o = OtherRule()

        class MyRule(OtherRule):
            async def test_async(self) -> None:
                await self.check_ctx_async()
                await o.check_ctx_async()

        await MyRule().test_async()
