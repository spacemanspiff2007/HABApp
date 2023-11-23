from __future__ import annotations

import importlib
import sys

from HABApp.__debug_info__ import print_debug_info


def get_dependencies() -> list[str]:
    return [
        'aiohttp-sse-client',
        'aiohttp',
        'aiomqtt',
        'bidict',
        'colorama',
        'eascheduler',
        'easyconfig',
        'pydantic',
        'stack_data',
        'voluptuous',
        'watchdog',
        'ujson',
        'immutables',
        'javaproperties',
        'msgspec',
        'pendulum',

        'typing-extensions',
    ]


def check_dependency_packages():
    """Imports all dependencies and reports failures"""

    missing: dict[str, ModuleNotFoundError] = {}

    # Package aliases (if the import name differs from the package name)
    alias = {
        'aiohttp-sse-client': 'aiohttp_sse_client',
        'paho-mqtt': 'paho.mqtt',
        'typing-extensions': 'typing_extensions',
    }

    for name in get_dependencies():
        try:
            importlib.import_module(alias.get(name, name))
        except ModuleNotFoundError as e:  # noqa: PERF203
            missing[name] = e

    if not missing:
        return None

    print_debug_info()
    print()

    print(f'Error: {len(missing)} package{"s are" if len(missing) != 1 else " is"} missing:')
    for name, err in missing.items():
        print(f' - {name}: {err}')

    sys.exit(100)
