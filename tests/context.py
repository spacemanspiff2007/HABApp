import os
import sys
__path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if __path not in sys.path:
    sys.path.insert(0, __path)

import HABApp

if __name__ == "__main__":
    import unittest

    testSuite = unittest.defaultTestLoader.discover(
        start_dir=os.path.abspath(os.path.join(os.path.dirname(__file__))),
        top_level_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    text_runner = unittest.TextTestRunner().run(testSuite)