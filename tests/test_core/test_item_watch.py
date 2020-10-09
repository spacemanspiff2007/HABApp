import HABApp
from HABApp.core.items import Item


class DummyRule:
    def register_cancel_obj(self, obj):
        pass


def test_multiple_add(monkeypatch):
    monkeypatch.setattr(HABApp.rule, 'get_parent_rule', lambda: DummyRule(), raising=True)

    i = Item('test')
    w1 = i.watch_change(5)
    w2 = i.watch_change(5)

    assert w1 is w2

    w1._fut.cancel()
    w2 = i.watch_change(5)
    assert w1 is not w2
