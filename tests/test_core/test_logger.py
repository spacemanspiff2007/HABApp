from HABApp.core.logger import HABAppLogger, HABAppError, HABAppInfo, HABAppWarning
from logging import getLogger


def test_exception():
    e = Exception('Exception test')
    assert HABAppLogger(None).add_exception(e).lines == ['Exception test']


def test_exception_multiline():
    e = Exception('Line1\nLine2\nLine3')
    assert HABAppLogger(None).add_exception(e).lines == ['Line1', 'Line2', 'Line3']


def test_exception_traceback():
    e = Exception('Line1\nLine2\nLine3')
    assert HABAppLogger(None).add_exception(e, add_traceback=True).lines == ['Exception: Line1', 'Line2', 'Line3']


def test_bool():
    for cls in (HABAppError, HABAppInfo, HABAppWarning):
        i = cls(getLogger('test')).add('')
        assert i
        i.dump()
        assert not i
