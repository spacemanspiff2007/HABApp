import logging

from HABAppTests import TestBaseRule

import HABApp


log = logging.getLogger('HABApp.TestParameterFiles')

# User Parameter files to create rules dynamically
assert HABApp.DictParameter('param_file') == {'key': 10}
assert HABApp.Parameter('param_file', 'key') == 10


class TestParamFile(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.add_test('ParamFile', self.test_param_file)

    def test_param_file(self) -> None:
        p = HABApp.Parameter('param_file', 'key')
        assert p.value == 10
        assert p < 11
        assert p > 9

        p = HABApp.DictParameter('param_file')
        assert p == {'key': 10}


TestParamFile()
