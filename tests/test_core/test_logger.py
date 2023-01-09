from logging import getLogger
from unittest.mock import Mock

from HABApp.core.logger import HABAppLogger, HABAppError, HABAppInfo, HABAppWarning
from tests.helpers import TestEventBus


def test_exception():
    e = Exception('Exception test')
    assert HABAppLogger(None).add_exception(e).lines == ['Exception test']


def test_exception_multiline():
    e = Exception('Line1\nLine2\nLine3')
    assert HABAppLogger(None).add_exception(e).lines == ['Line1', 'Line2', 'Line3']


def test_exception_traceback():
    try:
        raise Exception('Line1\nLine2\nLine3')
    except Exception as e:
        e = HABAppLogger(None).add_exception(e, add_traceback=True)
        assert e.lines


def test_bool(eb: TestEventBus):
    eb.allow_errors = True

    for cls in (HABAppError, HABAppInfo, HABAppWarning):
        i = cls(getLogger('test')).add('')
        i.logger = Mock()
        assert i
        i.dump()
        assert not i
