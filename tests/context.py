import os, logging
import sys
__path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if __path not in sys.path:
    sys.path.insert(0, __path)

import HABApp


def add_stdout(logger_name=None):
    _log = logging.getLogger(logger_name)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter("[{asctime:s}] [{name:25s}] {levelname:8s} | {message:s}", style='{'))
    _log.addHandler(ch)


if __name__ == "__main__":
    import unittest

    add_stdout()

    testSuite = unittest.defaultTestLoader.discover(
        start_dir=os.path.abspath(os.path.join(os.path.dirname(__file__))),
        top_level_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    text_runner = unittest.TextTestRunner().run(testSuite)