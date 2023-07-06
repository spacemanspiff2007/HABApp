from typing import Dict

from HABApp.core.wrapper import ignore_exception, ExceptionToHABApp
# noinspection PyProtectedMember
from HABApp.openhab.transformations._map import MAP_REGISTRY
from HABApp.openhab.transformations.base import log, TransformationRegistryBase
from ._plugin import OnConnectPlugin
from ..connection_handler.func_async import async_get_transformations
from ..connection_handler.http_connection import OH_3


class LoadTransformations(OnConnectPlugin):

    @ignore_exception
    async def on_connect_function(self):
        if OH_3:
            log.info('Transformations are not supported on openHAB 3')
            return None

        exception_handler = ExceptionToHABApp(logger=log)

        log.debug('Requesting transformations')
        objs = await async_get_transformations()
        transformation_count = len(objs)
        log.debug(f'Got response with {transformation_count} transformation{"" if transformation_count == 1 else ""}')

        registries: Dict[str, TransformationRegistryBase] = {
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


PLUGIN_LOAD_TRANSFORMATIONS = LoadTransformations.create_plugin()
