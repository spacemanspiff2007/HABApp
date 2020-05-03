import logging
from unittest.mock import MagicMock

import pytest

import HABApp
from HABApp.core.wrapper import ExceptionToHABApp, ignore_exception

log = logging.getLogger('WrapperTest')


@pytest.fixture
def p_mock():
    post_event = HABApp.core.EventBus.post_event
    HABApp.core.EventBus.post_event = m = MagicMock()
    yield m
    HABApp.core.EventBus.post_event = post_event


def test_error_catch(p_mock):

    p_mock.assert_not_called()

    with ExceptionToHABApp(log, logging.WARNING):
        pass
    p_mock.assert_not_called()

    with ExceptionToHABApp(log, logging.WARNING):
        1 / 0
    p_mock.assert_called_once()
    assert p_mock.call_args[0][0] == HABApp.core.const.topics.WARNINGS


def test_error_level(p_mock):
    with ExceptionToHABApp(log, logging.WARNING):
        1 / 0
    p_mock.assert_called_once()
    assert p_mock.call_args[0][0] == HABApp.core.const.topics.WARNINGS

    p_mock.reset_mock()

    with ExceptionToHABApp(log):
        1 / 0
    p_mock.assert_called_once()
    assert p_mock.call_args[0][0] == HABApp.core.const.topics.ERRORS


@ignore_exception
def func_a(_l):
    1 / 0


def test_func_wrapper():
    func_a(['asdf', 'asdf'])
