import time

from HABAppTests import ItemWaiter, TestBaseRule

from HABApp.core.items import Item
from HABApp.util.fade.fade import Fade


class TestFadeRun(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self):
        super().__init__()

        self.add_test('TestFade', self.test_fade)

    def test_fade(self):
        item = Item.get_create_item('TestFadeItem')
        item.set_value(None)

        vals = {}
        now = time.time()

        def add_value(v):
            vals[time.time() - now] = v
            item.set_value(v)

        f = Fade(callback=add_value)
        f.setup(0, 10, 3)
        f.schedule_fade()

        ItemWaiter(item, 3.1).wait_for_state(10.0)

        assert f._fade_worker is None
        assert len(vals) == 10  # 10 fade steps


TestFadeRun()
