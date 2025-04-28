import functools
import logging
from asyncio import sleep
from collections.abc import Callable, Coroutine, Sequence
from inspect import iscoroutinefunction
from types import TracebackType
from typing import Any, Final

import HABApp
from HABApp.core.events import NoEventFilter
from HABApp.core.internals import EventBusListener, WrappedFunctionBase, wrap_func
from HABAppTests.test_rule._com_patcher import BasePatcher, MqttPatcher, RestPatcher, WebsocketPatcher
from HABAppTests.test_rule.test_result import TestResult, TestResultStatus
from HABAppTests.utils import get_file_path_of_obj


class TmpLogLevel:
    def __init__(self, name: str) -> None:
        self.log = logging.getLogger(name)
        self.old = self.log.level

    def __enter__(self) -> None:
        self.old = self.log.level
        self.log.setLevel(logging.INFO)

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        self.log.setLevel(self.old)
        return False


class ExecutionEventCatcher:
    def __init__(self, event_name: str, event_bus_name: str) -> None:
        self._event_name: Final = event_name
        self._event_bus_name: Final = event_bus_name

        self._listener: EventBusListener | None = None
        self._events = []

    async def _event(self, event: Any) -> None:
        self._events.append(event)

    def get_message(self) -> str:
        if not self._events:
            return ''
        return f'{(ct := len(self._events))} {self._event_name}{"s" if ct != 1 else ""} in worker'

    async def __aenter__(self):
        if self._listener is None:
            ebl = EventBusListener(self._event_bus_name, wrap_func(self._event), NoEventFilter())
            self._listener = ebl

            with TmpLogLevel('HABApp'):
                HABApp.core.EventBus.add_listener(ebl)

        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        if (ebl := self._listener) is not None:
            self._listener = None
            with TmpLogLevel('HABApp'):
                ebl.cancel()
        return False


def tc_wrap_func(func: Callable | Callable[[...], Coroutine], res: TestResult) -> WrappedFunctionBase:
    if iscoroutinefunction(func):
        @functools.wraps(func)
        async def tc_async_wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                res.exception(e)
                return None

        return wrap_func(tc_async_wrapped)

    @functools.wraps(func)
    def tc_wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            res.exception(e)
            return None

    return wrap_func(tc_wrapped)


class TestCase:
    def __init__(self, name: str, func: Callable | Callable[[...], Coroutine],
                 args: Sequence[Any] = (), kwargs: dict[str, Any] | None = None,
                 setup_up: Callable | Callable[[...], Coroutine] | None = None,
                 tear_down: Callable | Callable[[...], Coroutine] | None = None) -> None:
        self.name: Final = name
        self.func: Final = func
        self.args: Final = args
        self.kwargs: Final = kwargs if kwargs is not None else {}

        self.set_up: Final = setup_up if setup_up is not None else None
        self.tear_down: Final = tear_down if tear_down is not None else None

    async def run(self, res: TestResult) -> TestResult:

        async with ExecutionEventCatcher('warning', HABApp.core.const.topics.TOPIC_WARNINGS) as worker_warnings, \
                   ExecutionEventCatcher('error', HABApp.core.const.topics.TOPIC_ERRORS) as worker_errors:

            try:
                suffix = f' (from "{get_file_path_of_obj(self.func)}")'
            except ValueError:
                suffix = ''

            name = RestPatcher.create_name(f'{res.group_name:s}.{res.test_name:s}{suffix:s}')
            b = BasePatcher(name, 'TC')

            try:
                with RestPatcher(name), MqttPatcher(name), WebsocketPatcher(name):
                    if s := self.set_up:
                        await tc_wrap_func(s, res).async_run()
                        await sleep(0.1)
                        b.log('Setup done')

                    ret = await tc_wrap_func(self.func, res).async_run(*self.args, **self.kwargs)
                    if ret:
                        res.set_state(TestResultStatus.FAILED)
                        res.add_msg(f'{ret}')
                    else:
                        res.set_state(TestResultStatus.PASSED)

                await sleep(0.1)
            except Exception as e:
                res.exception(e)

            try:
                if t := self.tear_down:
                    b.log('Tear down')
                    await tc_wrap_func(t, res).async_run()
                    await sleep(0.1)
            except Exception as e:
                res.exception(e)

        await sleep(0.1)

        if msg := worker_warnings.get_message():
            res.set_state(TestResultStatus.WARNING)
            res.add_msg(msg)

        if msg := worker_errors.get_message():
            res.set_state(TestResultStatus.ERROR)
            res.add_msg(msg)

        return res


log = logging.getLogger('HABApp.Tests')


async def run_test_cases(test_cases: Sequence[TestCase], group_name: str, source: str | object, *,
                         skip_on_failure: bool = False) -> list[TestResult]:
    source_text = source if isinstance(source, str) else get_file_path_of_obj(source)

    count = len(test_cases)
    width = len(str(count))

    results = [TestResult(group_name, tc.name, f'{i:{width}d}/{count}') for i, tc in enumerate(test_cases, 1)]

    log.info('')
    log.info(
        f'Running {count:d} test{"s" if count != 1 else ""} for {group_name:s}  (from "{source_text:s}")'
    )

    for res, tc in zip(results, test_cases, strict=True):
        if skip_on_failure and max(r.state for r in results) >= TestResultStatus.FAILED:
            res.set_state(TestResultStatus.SKIPPED)
            res.log()
            continue

        await tc.run(res)
        res.log()

    return results
