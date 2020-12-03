import typing
from pathlib import Path

import setuptools  # type: ignore


# Load version number without importing HABApp
def load_version() -> str:
    version: typing.Dict[str, str] = {}
    with open("HABApp/__version__.py") as fp:
        exec(fp.read(), version)
    assert version['__version__'], version
    return version['__version__']


def load_req() -> typing.List[str]:
    # When we run tox tests we don't have this file available so we skip them
    req_file = Path(__file__).with_name('requirements.txt')
    if not req_file.is_file():
        return ['']

    with req_file.open() as f:
        return f.readlines()


__version__ = load_version()

print(f'Version: {__version__}')
print('')

# When we run tox tests we don't have these files available so we skip them
readme = Path(__file__).with_name('readme.md')
long_description = ''
if readme.is_file():
    with readme.open("r", encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name="HABApp",
    version=__version__,
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
    install_requires=load_req(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Home Automation"
    ],
    entry_points={
        'console_scripts': [
            'habapp = HABApp.__main__:main'
        ]
    }
)
