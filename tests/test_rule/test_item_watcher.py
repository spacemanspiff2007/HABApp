import unittest
import time
from datetime import datetime, timedelta

import HABApp
from HABApp import Rule

from ..rule_runner import SimpleRuleRunner


class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.runner = SimpleRuleRunner()
        self.rule: Rule = None

        self.event_triggered = False

    def setUp(self):

        self.runner.set_up()
        self.rule = Rule()

    def tearDown(self):
        self.runner.tear_down()
        self.rule = None

    def run_no_change_event(self, event):
        assert isinstance(event, HABApp.core.events.ValueNoChangeEvent)
        self.assertEqual(event.seconds, 2)

        self.event_triggered = True

    def run_no_update_event(self, event):
        assert isinstance(event, HABApp.core.events.ValueNoUpdateEvent)
        self.assertEqual(event.seconds, 2)

        self.event_triggered = True

    def test_watcher_changes(self):
        self.event_triggered = False

        watcher, listener = self.rule.item_watch_and_listen('test_watch', 2, self.run_no_change_event)
        HABApp.core.Items.create_item('test_watch', HABApp.core.items.Item, 'asdf')

        now = datetime.now()
        for delta in [timedelta(seconds=-2), timedelta(), timedelta(seconds=1)]:
            self.rule.set_item_state('test_watch', 'asdf')
            self.event_triggered = False
            self.rule._process_events(now + delta)
            time.sleep(0.01)
            self.assertFalse(self.event_triggered)

        self.rule._process_events(now + timedelta(seconds=2))
        time.sleep(0.01)
        self.assertTrue(self.event_triggered)

        now = datetime.now()
        for delta in [timedelta(seconds=2), timedelta(), timedelta(seconds=1)]:
            self.rule.set_item_state('test_watch', 'asdf')
            self.event_triggered = False
            self.rule._process_events(now + delta)
            time.sleep(0.01)
            self.assertFalse(self.event_triggered)

        watcher.cancel()


    def test_watcher_updates(self):
        self.event_triggered = False

        watcher, listener = self.rule.item_watch_and_listen(
            'test_watch', 2, self.run_no_update_event, watch_only_changes=False
        )
        HABApp.core.Items.create_item('test_watch', HABApp.core.items.Item, 'asdf')

        now = datetime.now()
        for delta in [timedelta(seconds=-2), timedelta(), timedelta(seconds=1)]:
            self.rule.set_item_state('test_watch', 'asdf')
            self.event_triggered = False
            self.rule._process_events(now + delta)
            time.sleep(0.01)
            self.assertFalse(self.event_triggered)

        self.rule._process_events(now + timedelta(seconds=2))
        time.sleep(0.01)
        self.assertFalse(self.event_triggered)

        now = datetime.now()
        for delta in [timedelta(seconds=1), timedelta(), timedelta(seconds=1)]:
            self.rule.set_item_state('test_watch', 'asdf')
            self.event_triggered = False
            self.rule._process_events(now + delta)
            time.sleep(0.01)
            self.assertFalse(self.event_triggered)

        self.rule._process_events(now + timedelta(seconds=3))
        time.sleep(0.01)
        self.assertTrue(self.event_triggered)

        watcher.cancel()



if __name__ == '__main__':
    unittest.main()
