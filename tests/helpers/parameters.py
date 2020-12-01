from pathlib import Path

import pytest

import HABApp
import HABApp.parameters.parameters as Parameters


@pytest.fixture(scope="function")
def params():
    class DummyCfg:
        class directories:
            param: Path = Path(__file__).parent

    original = HABApp.CONFIG
    HABApp.CONFIG = DummyCfg
    # Parameters.ParameterFileWatcher.UNITTEST = True
    # Parameters.setup(None, None)
    yield Parameters
    Parameters._PARAMETERS.clear()

    # delete possible created files
    for f in DummyCfg.directories.param.iterdir():
        if f.name.endswith('.yml'):
            f.unlink()

    HABApp.CONFIG = original
    return None
