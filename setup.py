from pathlib import Path
import setuptools

readme = Path(__file__).with_name('readme.md')
with open(readme, "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HABApp",
    version="0.0.1",
    author="spaceman_spiff",
    #author_email="",
    description="Easy auomations with openHAB.\nHABApp allows the creation of rules in pure python.",
    keywords = 'openHAB',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spacemanspiff2007/HABApp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only"
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)