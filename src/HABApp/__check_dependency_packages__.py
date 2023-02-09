import importlib
import sys
from typing import List, Dict

from HABApp.__debug_info__ import print_debug_info


def get_dependencies() -> List[str]:
    return [
        'aiohttp-sse-client',
        'aiohttp',
        'bidict',
        'colorama',
        'eascheduler',
        'easyconfig',
        'paho-mqtt',
        'pydantic',
        'stack_data',
        'voluptuous',
        'watchdog',
        'ujson',
        'immutables',
        'pendulum',

        'typing-extensions',
    ]


def check_dependency_packages():
    """Imports all dependencies and reports failures"""

    missing: Dict[str, ModuleNotFoundError] = {}

    # Package aliases (if the import name differs from the package name)
    alias = {
        'aiohttp-sse-client': 'aiohttp_sse_client',
        'paho-mqtt': 'paho.mqtt',
        'typing-extensions': 'typing_extensions',
    }

    for name in get_dependencies():
        try:
            importlib.import_module(alias.get(name, name))
        except ModuleNotFoundError as e:
            missing[name] = e

    if not missing:
        return None

    print_debug_info()
    print()

    print(f'Error: {len(missing)} package{"s are" if len(missing) != 1 else " is"} missing:')
    for name, err in missing.items():
        print(f' - {name}: {err}')

    sys.exit(100)
