import logging

from HABAppTests import EventWaiter, ItemWaiter, TestBaseRule

from HABApp.openhab.events import ItemStateChangedEventFilter
from HABApp.openhab.items import ImageItem


log = logging.getLogger('HABApp.Tests')


class TestMaxImageSize(TestBaseRule):
    """This rule is testing the OpenHAB item types by calling functions and checking values"""

    def __init__(self) -> None:
        super().__init__()
        self.add_test('Test Image Size', self.test_img_size)

    def test_img_size(self) -> None:

        image = ImageItem.get_item('TestImage')
        image.oh_post_update(None)

        with ItemWaiter(image) as item_waiter, \
                EventWaiter(image.name, ItemStateChangedEventFilter()) as event_waiter:

            k = 95  # test data size in kib

            _b1 = b'\xFF\xD8\xFF' + b'\x00' * (1024 - 3) + b'\x00' * (k - 1) * 1024
            _b2 = b'\xFF\xD8\xFF' + b'\xFF' * (1024 - 3) + b'\x00' * (k - 1) * 1024

            image.oh_post_update(_b1)
            event_waiter.wait_for_event(value=_b1)
            item_waiter.wait_for_state(_b1)

            image.oh_post_update(_b2)
            event_waiter.wait_for_event(value=_b2, old_value=_b1)
            item_waiter.wait_for_state(_b2)

            log.info(f'Image with {len(_b2) / 1024:.0f}k ok!')


TestMaxImageSize()
