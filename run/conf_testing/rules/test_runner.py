import asyncio

from HABAppTests import TestResult, TestRunnerRule
from HABAppTests.test_rule.test_case import TestCase, run_test_cases

from HABApp import CONFIG
from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.events.habapp_events import RequestFileUnloadEvent
from HABApp.core.items import Item


class TestRunnerImpl(TestRunnerRule):

    def __init__(self) -> None:
        super().__init__()
        self._file_pos = 0

    async def tests_done(self, results: list[TestResult]) -> None:
        results.extend(
            await run_test_cases([TestCase('RuleLifeCycle', self.test_lifecycle_methods)], 'RuleLifeCycle', self)
        )

        # show errors of HABApp.log
        log_file = CONFIG.directories.logging / 'HABApp.log'

        seek = self._file_pos
        self._file_pos = log_file.stat().st_size

        with log_file.open('r') as f:
            f.seek(seek)
            text = f.read()

        show = []
        for line in text.splitlines():
            if ' ERROR ' in line:
                show.append(line)
                continue

            if ' WARNING ' in line:
                if 'DeprecationWarning' in line or 'is a UoM item but "unit" is not found in item metadata' in line:
                    continue
                if 'Item type changed from' in line:
                    continue
                show.append(line)

        if show:
            print('-' * 120)
            for line in show:
                print(line)
            print('-' * 120)
            print()

    async def test_lifecycle_methods(self) -> None:
        item = Item.get_item('RuleLifecycleMethods')

        assert item.value[0:2] == ['on_rule_loaded_thread', 'on_rule_loaded_task']

        self.post_event(TOPIC_FILES, RequestFileUnloadEvent('rules/habapp/test_internals.py'))
        await asyncio.sleep(1)

        assert item.value[2:4] == ['on_rule_removed_thread', 'on_rule_removed_task']


TestRunnerImpl()
