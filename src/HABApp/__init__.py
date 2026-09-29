# 1. Static stuff
from .__version__ import __version__


# isort: split

# 2. Setup used libraries and check installation
import HABApp.__setup_packages__

# 3. User configuration
import HABApp.config

# 4. Core features
import HABApp.core

# This holds only textual references to other objects so we can import this before everything else
import HABApp.rule_ctx


# isort: split

# Import the rest
import HABApp.mqtt
import HABApp.openhab
import HABApp.parameters
import HABApp.rule
import HABApp.runtime
import HABApp.util


# isort: split

from HABApp.config import CONFIG as CONFIG
from HABApp.rule import Rule as Rule


# isort: split

# Deprecated imports - kept for backwards compatibility
import typing
import warnings


if typing.TYPE_CHECKING:
    from HABApp.parameters import DictParameter as DictParameter
    from HABApp.parameters import Parameter as Parameter


def __getattr__(name: str) -> typing.Any:
    if name in ('Parameter', 'DictParameter'):
        warnings.warn(
            f'HABApp.{name} is deprecated, use HABApp.parameters.{name} instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(HABApp.parameters, name)

    msg = f'module {__name__!r} has no attribute {name!r}'
    raise AttributeError(msg)
