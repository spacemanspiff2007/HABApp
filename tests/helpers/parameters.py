import time
from pathlib import Path

import pytest

import HABApp
import HABApp.parameters.parameters as Parameters


@pytest.fixture(scope='function')
def params():
    class DummyCfg:
        class directories:
            params: Path = Path(__file__).parent

    original = HABApp.CONFIG
    HABApp.CONFIG = DummyCfg

    yield Parameters

    # Clean parameters so they are empty for the next test
    Parameters._PARAMETERS.clear()

    # delete possible created files
    to_delete = list(filter(lambda _f: _f.name.endswith('.yml'), DummyCfg.directories.params.iterdir()))
    if to_delete:
        time.sleep(0.1)
        for f in to_delete:
            f.unlink()

    HABApp.CONFIG = original
    return None
