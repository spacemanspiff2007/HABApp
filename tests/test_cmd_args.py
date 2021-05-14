from datetime import timedelta
from unittest.mock import Mock

import pytest

from HABApp import __cmd_args__


def test_get_uptime():
    __cmd_args__.get_uptime()


@pytest.mark.parametrize('arg_name', ('-wos', '--wait_os_uptime'))
def test_cmd_wait_uptime(monkeypatch, arg_name):
    td = timedelta(days=110 * 365)

    m = Mock()
    monkeypatch.setattr(__cmd_args__.time, 'sleep', m)
    monkeypatch.setattr(__cmd_args__, 'find_config_folder', lambda x: x)

    __cmd_args__.parse_args(['-w', f'{int(td.total_seconds())}'])

    # get first func call
    args = m.call_args[0]
    waited = timedelta(seconds=args[0])
    assert waited.days > 100 * 365
