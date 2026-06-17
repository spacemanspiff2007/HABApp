from __future__ import annotations

from typing import Final

from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.wrapper import ExceptionToHABApp
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.connection.handler import OpenHabAsyncInterface
from HABApp.openhab.transformations._map import MAP_REGISTRY
from HABApp.openhab.transformations.base import TransformationRegistryBase, log


class LoadTransformationsPlugin(BaseConnectionPlugin[OpenhabConnection]):
    def __init__(self, *, name: str | None = None, interface: OpenHabAsyncInterface) -> None:
        super().__init__(name)
        self._interface: Final = interface

    async def on_connected(self) -> None:
        exception_handler = ExceptionToHABApp(logger=log)

        log.debug('Requesting transformations')
        objs = await self._interface.get_transformations()
        transformation_count = len(objs)
        log.debug(f'Got response with {transformation_count} transformation{"" if transformation_count == 1 else "s"}')

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
