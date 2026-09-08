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
import HABApp.rule
import HABApp.runtime
import HABApp.util


# isort: split

from HABApp.config import CONFIG as CONFIG
from HABApp.parameters import BaseModelParameter as BaseModelParameter
from HABApp.parameters import DictParameter as DictParameter
from HABApp.parameters import FloatParameter as FloatParameter
from HABApp.parameters import IntParameter as IntParameter
from HABApp.parameters import NumberParameter as NumberParameter
from HABApp.parameters import Parameter as Parameter
from HABApp.parameters import StrParameter as StrParameter
from HABApp.rule import Rule as Rule
