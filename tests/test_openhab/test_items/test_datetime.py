from datetime import datetime

from whenever import PlainDateTime

from HABApp.openhab.items import DatetimeItem


def test_post_update(websocket_events) -> None:
    item = DatetimeItem('')

    item.oh_post_update(datetime(2025, 1, 1, 12, 0, 1))
    websocket_events.assert_called_once('DateTime', '2025-01-01T12:00:01', event='update')

    item.oh_post_update(PlainDateTime(2025, 1, 1, 12, 0, 1))
    websocket_events.assert_called_once('DateTime', '2025-01-01T12:00:01', event='update')

    item.oh_post_update('2025-02-17T20:00:00Z')
    websocket_events.assert_called_once('DateTime', '2025-02-17T20:00:00Z', event='update')
