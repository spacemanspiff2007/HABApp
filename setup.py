from pathlib import Path
import setuptools

# Load version number
version = {}
with open("HABApp/__version__.py") as fp:
    exec(fp.read(), version)
assert version
assert version['__VERSION__']
__VERSION__ = version['__VERSION__']
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
    keywords='MQTT,openHAB,habapp,mqtt,home,automation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spacemanspiff2007/HABApp",
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=[
        'aiohttp',
        'aiohttp-sse-client',
        'ruamel.yaml',
        'paho-mqtt',
        'ujson',
        'voluptuous',
        'watchdog',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'habapp = HABApp.__main__:main'
        ]
    }
)
