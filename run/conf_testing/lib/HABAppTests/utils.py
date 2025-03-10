import random
import string
import time
import typing
from pathlib import Path

import HABApp
from HABApp.core.asyncio import run_coro_from_thread
from HABApp.openhab.connection.handler import post
from HABApp.openhab.items import Thing


__RAND_PREFIX = {
    'String': 'Str', 'Number': 'Num', 'Switch': 'Sw', 'Contact': 'Con', 'Dimmer': 'Dim', 'Rollershutter': 'Rol',
    'Color': 'Col', 'DateTime': 'Dt', 'Location': 'Loc', 'Player': 'Pl', 'Group': 'Grp', 'Image': 'Img', 'Call': 'Call',
    'HABApp': 'Ha'
}


def __get_fill_char(skip: str, upper=False) -> str:
    skip += 'ilo'
    skip = skip.upper() if upper else skip.lower()

    letters = string.ascii_uppercase if upper else string.ascii_lowercase
    while (rnd := random.choice(letters)) in skip:
        pass
    return rnd


def get_random_name(item_type: str) -> str:
    name = name_prev = __RAND_PREFIX[item_type.split(':')[0]]

    for _ in range(3):
        name += __get_fill_char(name_prev, upper=True)

    while len(name) < 10:
        name += __get_fill_char(name_prev)
    return name


def get_random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters, k=length))


def find_astro_sun_thing(*, create: bool = True) -> str:
    items = HABApp.core.Items.get_items()
    for item in items:
        if isinstance(item, Thing) and item.name.startswith('astro:sun'):
            return item.name

    if not create:
        msg = 'No astro thing found!'
        raise ValueError(msg)

    data = {
        'UID': 'astro:sun:habapp-testing',
        'label': 'Astronomische Sonnendaten',
        'configuration': {'geolocation': '52.5185537,13.3758636'},
        'channels': [],
        'thingTypeUID': 'astro:sun',
        'ID': 'habapp-testing'
    }

    resp = run_coro_from_thread(post('/rest/things', json=data), calling=find_astro_sun_thing)

    if resp.status != 201:
        msg = f'Could not create astro thing! {resp.text}'
        raise ValueError(msg)

    print('Created new astro thing for testing')
    time.sleep(2)

    return find_astro_sun_thing(create=False)


def get_file_path_of_obj(obj: typing.Any) -> str:
    try:
        module = obj.__module__
    except AttributeError:
        module = obj.__class__.__module__

    module_of_class = Path(module)
    return str(module_of_class.relative_to(HABApp.CONFIG.directories.rules))
