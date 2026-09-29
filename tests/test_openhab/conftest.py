from unittest.mock import Mock

import pytest

from HABApp.openhab.connection.handler import OpenHabSyncInterface


@pytest.fixture
def oh_interface() -> OpenHabSyncInterface:
    return Mock(OpenHabSyncInterface)
