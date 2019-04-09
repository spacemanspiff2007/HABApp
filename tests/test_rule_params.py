import unittest

from HABApp.rule.rule_parameter import RuleParameter, RuleParameters


class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params: RuleParameters = None

    def setUp(self):
        RuleParameters.UNITTEST = True
        self.params = RuleParameters(None, None)

    def tearDown(self):
        RuleParameters.UNITTEST = False

    def test_lookup(self):
        self.params.params['file1'] = {'key1': {'key2': 'value2'}}
        p = RuleParameter(self.params, 'file1', 'key1', 'key2')
        self.assertEqual(p, 'value2')

        self.params.params['file1']['key1']['key2'] = 3
        self.assertEqual(p, 3)

    def test_int_operators(self):
        self.params.params['file'] = {'key': 5}
        p = RuleParameter(self.params, 'file', 'key')
        self.assertEqual(p, 5)
        self.assertNotEqual(p, 6)

        self.assertTrue(p < 6)
        self.assertTrue(p <= 5)
        self.assertTrue(p >= 5)
        self.assertTrue(p > 4)

        self.params.params['file'] = {'key': 15}
        self.assertFalse(p < 6)
        self.assertFalse(p <= 5)
        self.assertTrue(p >= 5)
        self.assertTrue(p > 4)

    def test_float_operators(self):
        self.params.params['file'] = {'key': 5.5}
        p = RuleParameter(self.params, 'file', 'key')

        self.assertTrue(p < 6)
        self.assertFalse(p <= 5)
        self.assertTrue(p >= 5)
        self.assertTrue(p > 4)

    def test_simple_key_creation(self):
        RuleParameter(self.params, 'file', 'key')
        self.assertEqual(self.params.params, {'file': {'key': 'ToDo'}})
        RuleParameter(self.params, 'file', 'key2')
        self.assertEqual(self.params.params, {'file': {'key': 'ToDo', 'key2': 'ToDo'}})

    def test_structured_key_creation(self):
        RuleParameter(self.params, 'file', 'key1', 'key1')
        RuleParameter(self.params, 'file', 'key1', 'key2')
        self.assertEqual(self.params.params, {'file': {'key1': {'key1': 'ToDo', 'key2': 'ToDo'}}})

    def test_structured_default_value(self):
        RuleParameter(self.params, 'file', 'key1', 'key1', default_value=123)
        RuleParameter(self.params, 'file', 'key1', 'key2', default_value=[1, 2, 3])
        self.assertEqual(self.params.params, {'file': {'key1': {'key1': 123, 'key2': [1, 2, 3]}}})


if __name__ == '__main__':
    unittest.main()
