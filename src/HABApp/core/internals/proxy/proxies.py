from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from HABApp.core.internals.proxy.proxy_obj import create_proxy, replace_proxies


if TYPE_CHECKING:
    import HABApp


def uses_post_event() -> Callable[[str, Any], None]:
    return create_proxy(uses_post_event)


def uses_event_bus() -> 'HABApp.core.internals.EventBus':
    return create_proxy(uses_event_bus)


def uses_get_item() -> Callable[[str], 'HABApp.core.internals.item_registry.item_registry.ItemRegistryItem']:
    return create_proxy(uses_get_item)


def uses_item_registry() -> 'HABApp.core.internals.ItemRegistry':
    return create_proxy(uses_item_registry)


def uses_file_manager() -> 'HABApp.core.files.FileManager':
    return create_proxy(uses_file_manager)


def setup_internals(ir: 'HABApp.core.internals.ItemRegistry',
                    eb: 'HABApp.core.internals.EventBus',
                    file_manager: 'HABApp.core.files.FileManager', final=True):
    """Replace the proxy objects with the real thing"""
    replacements = {
        uses_item_registry: ir, uses_get_item: ir.get_item,
        uses_event_bus: eb, uses_post_event: eb.post_event,
        uses_file_manager: file_manager,
    }
    return replace_proxies(replacements, final=final)
