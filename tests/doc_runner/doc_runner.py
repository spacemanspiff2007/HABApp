import asyncio
import traceback
from collections.abc import Awaitable, Callable, Generator
from datetime import datetime
from typing import Any, Final

import pytest
from _pytest.fixtures import FixtureFunctionDefinition
from _pytest.monkeypatch import MonkeyPatch
from pytest import MonkeyPatch  # noqa: PT013
from whenever import PlainDateTime, ZonedDateTime

from HABApp.core.internals.function_executor.testing import TestingExecutorFactory
from HABApp.core.provider import HabAppObjProvider
from HABApp.core.provider.provider import T
from HABApp.testing import TestingStartTimeOptions
from HABApp.testing import conftest as conftest_module


class DocHabAppObjProvider(HabAppObjProvider):
    def register(self, obj: T) -> T:
        # add support for unpacking pytest fixtures so we can reuse them
        if isinstance(obj, FixtureFunctionDefinition):
            obj = obj._get_wrapped_function()

        return super().register(obj)


def run(doc_func: Callable[[HabAppObjProvider], Awaitable[Any]],
        start_time: datetime | None = None, keep_ticking: bool = False) -> None:

    if start_time is not None:
        time_obj = PlainDateTime.from_py_datetime(start_time).assume_tz('Europe/Berlin', disambiguate='raise')
    else:
        time_obj = ZonedDateTime.now('Europe/Berlin').replace(
            month=1, day=15, hour=14, minute=0, second=0, nanosecond=0
        )

    asyncio.run(main(doc_func, start_time=time_obj, keep_ticking=keep_ticking))


async def main(doc_func: Callable[[HabAppObjProvider], Awaitable[Any]], *,
               start_time: ZonedDateTime, keep_ticking: bool):

    def testing_start_time() -> TestingStartTimeOptions:
        return TestingStartTimeOptions(start=start_time, keep_ticking=keep_ticking)

    overrides: Final = (testing_start_time, )
    override_names: Final = tuple(f.__name__ for f in overrides)

    provider: Final = DocHabAppObjProvider()

    # register dependencies that normally come from pytest
    provider.register(provide_mp)

    # register all testing objects
    for name in conftest_module.__all__:
        if name not in override_names:
            provider.register(getattr(conftest_module, name))

    for obj in overrides:
        provider.register(obj)

    async with asyncio.timeout(10):
        await provider.create_all()
        await doc_func(provider)

    factory = await provider.get(TestingExecutorFactory)
    if factory.errors:
        msgs = ['\n'.join(traceback.format_exception(e)) for e in factory.errors]
        raise RuntimeError(('\n' + '-' * 80 + '\n').join(msgs))


def provide_mp() -> Generator[MonkeyPatch, Any, None]:
    mp = pytest.MonkeyPatch()
    yield mp
    mp.undo()
