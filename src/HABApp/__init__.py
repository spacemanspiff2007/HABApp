# 1. Static stuff
from .__version__ import __version__

# 2. Setup used libraries and check installation
import HABApp.__setup_packages__

# 3. User configuration
import HABApp.config

# 4. Core features
import HABApp.core

# This holds only textual references to other objects so we can import this before everything else
import HABApp.rule_ctx


# Import the rest
import HABApp.mqtt
import HABApp.openhab
import HABApp.rule
import HABApp.runtime


import HABApp.util
from HABApp.rule import Rule
from HABApp.parameters import Parameter, DictParameter

from HABApp.config import CONFIG
