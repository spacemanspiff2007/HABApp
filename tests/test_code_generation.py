import HABApp.core.events as events_module
import HABApp.openhab.definitions.websockets.all_events as all_events_module
import HABApp.openhab.definitions.websockets.item_value_types as item_value_types_module
import HABApp.openhab.events as oh_events_module
from tests.helpers.code_gen import run_code_generator


def test_run_code_generator() -> None:

    run_code_generator(events_module)
    run_code_generator(all_events_module)
    run_code_generator(oh_events_module)
    run_code_generator(item_value_types_module)
    run_code_generator(item_value_types_module)
