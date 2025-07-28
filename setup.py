import re
from pathlib import Path

from setuptools import find_packages, setup


THIS_FILE = Path(__file__)


# Load version number without importing HABApp
def load_version() -> str:
    version: dict[str, str] = {}
    exec((THIS_FILE.parent / 'src/HABApp/__version__.py').read_text(), version)  # noqa: S102
    assert version['__version__'], version
    return version['__version__']


def load_req() -> list[str]:

    lines = THIS_FILE.with_name('requirements_setup.txt').read_text().splitlines()
    print(lines)

    for i, line in enumerate(lines):
        if m := re.search(r'([^/]+).git@\w', line):
            lines[i] = f'{m.group(1):s} @ {line:s}'
            print(f'Modified: {lines[i]}')
    return lines


__version__ = load_version()

print(f'Version: {__version__}')
print()


# When we run tox tests we don't have these files available, so we skip them
readme = THIS_FILE.with_name('readme.md')
long_description = ''
if readme.is_file():
    with readme.open('r', encoding='utf-8') as fh:
        long_description = fh.read()

setup(
    name='HABApp',
    version=__version__,
    author='spaceman_spiff',
    # author_email="",
    description='Easy automation with MQTT and/or openHAB. Create home automation rules in python.',
    keywords=[
        'mqtt',
        'openhab',
        'habapp',
        'home automation'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/spacemanspiff2007/HABApp',
    project_urls={
        'Documentation': 'https://habapp.readthedocs.io/',
        'GitHub': 'https://github.com/spacemanspiff2007/HABApp',
    },
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests*']),
    package_data={'HABApp': ['py.typed']},
    install_requires=load_req(),
    python_requires='>=3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Home Automation'
    ],
    entry_points={
        'console_scripts': [
            'habapp = HABApp.__main__:main'
        ]
    }
)
