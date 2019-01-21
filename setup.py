import HABApp

from pathlib import Path
import setuptools

# don't load file for tox-builds
readme = Path(__file__).with_name('readme.md')
long_description = ''
if readme.is_file():
    with open(readme, "r", encoding='utf-8') as fh:
        long_description = fh.read()

setuptools.setup(
    name="HABApp",
    version=HABApp.VERSION,
    author="spaceman_spiff",
    # author_email="",
    description="Easy automation with openHAB and/or MQTT. Create home automation rules in python.",
    keywords='openHAB,habapp,mqtt,home,automation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spacemanspiff2007/HABApp",
    packages=setuptools.find_packages(exclude=['tests*']),
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
