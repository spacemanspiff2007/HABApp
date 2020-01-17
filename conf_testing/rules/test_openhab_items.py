import logging

from HABAppTests import ItemWaiter, OpenhabTmpItem, TestBaseRule, get_openhab_test_states

from HABApp.openhab.definitions import ITEM_TYPES

log = logging.getLogger('HABApp.Tests')


class TestOpenhabExpire(TestBaseRule):

    def __init__(self):
        super().__init__()
        for _type in ITEM_TYPES:
            if _type == 'Group':
                continue
            self.add_test(f'Expire {_type}', self.test_expire, _type)

    def test_expire(self, _type):
        states = get_openhab_test_states(_type)
        start = states[0]
        soll = states[1]

        with OpenhabTmpItem(None, _type) as item, ItemWaiter(item) as waiter:
            item.expire(0.3, soll)
            self.oh.post_update(item, start)
            waiter.wait_for_state(soll)

            item.expire(None)
            if not waiter.states_ok:
                return False
            return True


TestOpenhabExpire()
