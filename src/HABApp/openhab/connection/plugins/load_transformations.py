from __future__ import annotations

from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.core.wrapper import ExceptionToHABApp
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler.func_async import async_get_transformations
from HABApp.openhab.transformations._map import MAP_REGISTRY
from HABApp.openhab.transformations.base import TransformationRegistryBase, log

Items = uses_item_registry()


class LoadTransformationsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    async def on_connected(self, context: OpenhabContext):
        if context.is_oh3:
            log.info('Transformations are not supported on openHAB 3')
            return None

        exception_handler = ExceptionToHABApp(logger=log)

        log.debug('Requesting transformations')
        objs = await async_get_transformations()
        transformation_count = len(objs)
        log.debug(f'Got response with {transformation_count} transformation{"" if transformation_count == 1 else ""}')

        registries: dict[str, TransformationRegistryBase] = {
            MAP_REGISTRY.name: MAP_REGISTRY
        }

        for reg in registries.values():
            reg.clear()

        for obj in objs:
            with exception_handler:
                if reg := registries.get(obj.type):
                    reg.set(obj.uid, obj.configuration)

        if not any(r.objs for r in registries.values()):
            log.info('No transformations available')
        else:
            log.info('Transformations:')
            for name, reg in registries.items():
                log.info(f'  {name.title()}: {", ".join(reg.available())}')
