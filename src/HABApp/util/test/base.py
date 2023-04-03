import unittest
import unittest.mock
from typing import Optional

from pendulum.datetime import DateTime

from .rule_runner import TimeAwareRuleRunner
from .oh_item import send_command


class BaseTest(unittest.TestCase):
    def get_start_time(self) -> Optional[DateTime]:
        return None

    def setUp(self) -> None:
        self.send_command_mock_patcher = unittest.mock.patch(
            "HABApp.openhab.items.base_item.send_command",
            new=send_command,
        )
        self.addCleanup(self.send_command_mock_patcher.stop)
        self.send_command_mock = self.send_command_mock_patcher.start()

        self._runner = TimeAwareRuleRunner(now=self.get_start_time())
        self._runner.set_up()

    def tearDown(self) -> None:
        self._runner.tear_down()
