import typing
from pathlib import Path

import setuptools


# Load version number without importing HABApp
def load_version() -> str:
    version: typing.Dict[str, str] = {}
    with open("HABApp/__version__.py") as fp:
        exec(fp.read(), version)
    assert version['__VERSION__'], version
    return version['__VERSION__']


__VERSION__ = load_version()

print(f'Version: {__VERSION__}')
print('')

# don't load file for tox-builds
readme = Path(__file__).with_name('readme.md')
long_description = ''
if readme.is_file():
    with readme.open("r", encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name="HABApp",
    version=__VERSION__,
    author="spaceman_spiff",
    # author_email="",
    description="Easy automation with MQTT and/or openHAB. Create home automation rules in python.",
    keywords=[
        'mqtt',
        'openhab',
        'habapp',
        'home automation'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spacemanspiff2007/HABApp",
    project_urls={
        'Documentation': 'https://habapp.readthedocs.io/',
        'GitHub': 'https://github.com/spacemanspiff2007/HABApp',
    },
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=[
        'easyco>=0.2.1',
        'aiohttp>=3.5.4',
        'voluptuous>=0.11.7',
        'aiohttp-sse-client',
        'paho-mqtt',
        'ujson',
        'watchdog',
        'astral>=2.1,<3',
        'pytz',
        'tzlocal',

        # Backports
        'dataclasses;python_version<"3.7"',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Home Automation"
    ],
    entry_points={
        'console_scripts': [
            'habapp = HABApp.__main__:main'
        ]
    }
)
