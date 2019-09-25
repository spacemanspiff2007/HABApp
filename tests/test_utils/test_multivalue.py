from HABApp.util import MultiModeItem

def test_diff_prio():
    p = MultiModeItem('TestItem')
    p.create_mode('modea', 1, '1234')
    p.create_mode('modeb', 2, '4567')

    p1 = p.get_mode('modea')
    p2 = p.get_mode('modeb')
    
    p1.set_value(5)
    assert p.state == '4567'

    p2.set_enabled(False)
    assert p.state == 5

    p2.set_enabled(True)
    assert p.state == '4567'

    p2.set_enabled(False)
    p2.set_value(8888)
    assert p.state == 8888

