from HABApp.core.internals.proxy.proxy_obj import create_proxy, replace_proxies
from typing import Callable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    import HABApp


def uses_post_event() -> Callable[[str, Any], None]:
    return create_proxy(uses_post_event)


def uses_event_bus() -> 'HABApp.core.internals.TYPE_EVENT_BUS':
    return create_proxy(uses_event_bus)


def uses_get_item() -> Callable[[str], 'HABApp.core.internals.TYPE_ITEM_OBJ']:
    return create_proxy(uses_get_item)


def uses_item_registry() -> 'HABApp.core.internals.TYPE_ITEM_REGISTRY':
    return create_proxy(uses_item_registry)


def setup_internals(
        ir: 'HABApp.core.internals.TYPE_ITEM_REGISTRY', eb: 'HABApp.core.internals.TYPE_EVENT_BUS', final=True):
    replacements = {
        uses_item_registry: ir, uses_get_item: ir.get_item,
        uses_event_bus: eb, uses_post_event: eb.post_event,
    }
    return replace_proxies(replacements, final=final)