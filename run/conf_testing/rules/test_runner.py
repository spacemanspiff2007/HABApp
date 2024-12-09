import asyncio

from HABAppTests import TestResult, TestRunnerRule
from HABAppTests.test_rule.test_case import TestCase, run_test_cases

from HABApp import CONFIG
from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.events.habapp_events import RequestFileUnloadEvent
from HABApp.core.items import Item


class TestRunnterImpl(TestRunnerRule):

    async def tests_done(self, results: list[TestResult]) -> None:
        results.extend(
            await run_test_cases([TestCase('RuleLifeCycle', self.test_lifecycle_methods)], 'RuleLifeCycle', self)
        )

        # show errors of HABApp.log
        log_file = CONFIG.directories.logging / 'HABApp.log'
        errors = [line for line in log_file.read_text() if ' ERROR ' in line]
        if errors:
            print('-' * 120)
            for line in errors:
                print(line)
            print('-' * 120)
            print()

    async def test_lifecycle_methods(self) -> None:
        item = Item.get_item('RuleLifecycleMethods')

        assert item.value == ['on_rule_loaded_thread', 'on_rule_loaded_task']

        self.post_event(TOPIC_FILES, RequestFileUnloadEvent('rules/habapp/test_internals.py'))
        await asyncio.sleep(1)

        assert item.value == [
            'on_rule_loaded_thread', 'on_rule_loaded_task',
            'on_rule_unloaded_thread', 'on_rule_unloaded_task'
        ]


TestRunnterImpl()
