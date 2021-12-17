from HABApp.__version__ import __version__


def show_screen():
    txt = r"""
    __  _____    ____  ___
   / / / /   |  / __ )/   |  ____  ____
  / /_/ / /| | / __  / /| | / __ \/ __ \
 / __  / ___ |/ /_/ / ___ |/ /_/ / /_/ /
/_/ /_/_/  |_/_____/_/  |_/ .___/ .___/
                         /_/   /_/
"""

    print(txt.strip('\n\r'))
    print(f'{" " * 37}{__version__}')
