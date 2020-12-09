import asyncio
import random
import string
import typing
from binascii import b2a_hex

import HABApp
from HABApp.openhab.items import Thing


def get_random_name() -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(20))


def run_coro(coro: typing.Coroutine):
    fut = asyncio.run_coroutine_threadsafe(coro, HABApp.core.const.loop)
    return fut.result()


def find_astro_sun_thing() -> str:
    items = HABApp.core.Items.get_all_items()
    for item in items:
        if isinstance(item, Thing) and item.name.startswith("astro:sun"):
            return item.name

    raise ValueError('No astro thing found!')


def get_bytes_text(value):
    if isinstance(value, bytes) and len(value) > 100 * 1024:
        return b2a_hex(value[0:100]).decode() + ' ... ' + b2a_hex(value[-100:]).decode()
    return value
