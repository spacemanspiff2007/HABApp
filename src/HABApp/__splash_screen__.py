from HABApp.__version__ import __version__


def show_screen():
    txt = r"""
  _   _    _    ____    _
 | | | |  / \  | __ )  / \   _ __  _ __
 | |_| | / _ \ |  _ \ / _ \ | '_ \| '_ \
 |  _  |/ ___ \| |_) / ___ \| |_) | |_) |
 |_| |_/_/   \_|____/_/   \_| .__/| .__/
                            |_|   |_|
"""

    print(txt.strip('\n\r'))
    print(f'{" " * 40}{__version__}')
