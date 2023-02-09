from colorama import just_fix_windows_console, deinit, Fore

from HABApp.__version__ import __version__


def show_screen():
    text = r"""
  _   _    _    ____    _
 | | | |  / \  | __ )  / \   _ __  _ __
 | |_| | / _ \ |  _ \ / _ \ | '_ \| '_ \
 |  _  |/ ___ \| |_) / ___ \| |_) | |_) |
 |_| |_/_/   \_|____/_/   \_| .__/| .__/
                            |_|   |_|
"""

    red = r"""
    _
   / \   _ __  _ __
  / _ \ | '_ \| '_ \
 / ___ \| |_) | |_) |
/_/   \_| .__/| .__/
        |_|   |_|
"""

    just_fix_windows_console()

    for line_text, line_red in zip(text.strip('\n\r').splitlines(), red.strip('\n\r').splitlines()):
        red = line_red.strip()
        assert line_text.endswith(red)
        print(f'{line_text[:-len(red)]:s}{Fore.RED}{line_text[-len(red):]}{Fore.RESET}')

    # Version nr
    print(f'{" " * 40}{__version__}')

    deinit()
