import asyncio
import random
import string
import typing
from binascii import b2a_hex

import HABApp
from HABApp.openhab.items import Thing


__RAND_PREFIX = {
    'String': 'Str', 'Number': 'Num', 'Switch': 'Sw', 'Contact': 'Con', 'Dimmer': 'Dim', 'Rollershutter': 'Rol',
    'Color': 'Col', 'DateTime': 'Dt', 'Location': 'Loc', 'Player': 'Pl', 'Group': 'Grp', 'Image': 'Img',
    'HABApp': 'Ha'
}


def __get_fill_char(skip: str, upper=False) -> str:
    skip += 'il'
    skip = skip.upper() if upper else skip.lower()
    rnd = random.choice(string.ascii_uppercase if upper else string.ascii_lowercase)
    while rnd in skip:
        rnd = random.choice(string.ascii_uppercase if upper else string.ascii_lowercase)
    return rnd


def get_random_name(item_type: str) -> str:
    name = name_prev = __RAND_PREFIX[item_type.split(':')[0]]

    for c in range(3):
        name += __get_fill_char(name_prev, upper=True)

    while len(name) < 10:
        name += __get_fill_char(name_prev)
    return name


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
        return b2a_hex(value[0:40]).decode() + ' ... ' + b2a_hex(value[-40:]).decode()
    return value
