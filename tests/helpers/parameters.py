import time
from collections.abc import Generator
from pathlib import Path
from typing import Any, Final
from unittest.mock import Mock

import pytest

from HABApp.core.internals import EventBus
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.parameters.registry import ParameterRegistry
from tests.helpers.habapp_config import get_dummy_cfg


@pytest.fixture
def params() -> Generator[ParameterRegistry, Any, None]:
    cfg: Final = get_dummy_cfg()
    cfg.directories.params = Path(__file__).parent

    registry: Final = ParameterRegistry(cfg, Mock(spec=EventBus))
    registry.setup(Mock())
    HABAPP_PROVIDER.add_object(registry, ParameterRegistry, override_factory=True)

    yield registry

    # Remove the registry again so the next test gets a clean one
    HABAPP_PROVIDER._created.pop(ParameterRegistry, None)

    # delete possible created files
    to_delete = list(filter(lambda _f: _f.name.endswith('.yml'), cfg.directories.params.iterdir()))
    if to_delete:
        time.sleep(0.1)
        for f in to_delete:
            f.unlink()

    return None
