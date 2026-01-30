import asyncio
import logging
import os
import sys

from HABApp.__cmd_args__ import find_config_folder, parse_args
from HABApp.__debug_info__ import print_debug_info
from HABApp.__splash_screen__ import show_screen
from HABApp.core.shutdown import ShutdownInfo


async def main() -> int | str:
    loop = asyncio.get_event_loop()
    loop.slow_callback_duration = 0.02

    show_screen()

    import HABApp.core.items.tmp_data
    from HABApp.config.models import ApplicationConfig
    from HABApp.core.provider import HABAPP_PROVIDER

    # todo: fix this
    HABApp.core.asyncio.loop = loop
    HABApp.core.items.tmp_data.loop = loop

    @HABAPP_PROVIDER.register
    def __get_config() -> ApplicationConfig:
        return HABApp.config.CONFIG

    HABAPP_PROVIDER.register(HABApp.core.internals.ItemRegistry)
    HABAPP_PROVIDER.register(HABApp.core.internals.EventBus)

    # This has to be done before we create HABApp because of the possible sleep time
    args = parse_args()

    if HABApp.__cmd_args__.DO_DEBUG:
        print_debug_info()
        sys.exit(0)

    log = logging.getLogger('HABApp')

    try:
        cfg_folder = find_config_folder(args.config)

        # see if we have user code (e.g. for additional logging configuration or additional setup)
        try:  # noqa: SIM105
            import HABAppUser  # noqa: F401, PLC0415
        except ModuleNotFoundError:
            pass

        shutdown = await HABAPP_PROVIDER.get(ShutdownInfo)

        tg = asyncio.TaskGroup()
        HABAPP_PROVIDER.add_object(tg, asyncio.TaskGroup)

        app = HABApp.runtime.Runtime()

        async with tg, HABAPP_PROVIDER:
            tg.create_task(app.start(cfg_folder))
            tg.create_task(shutdown.wait_for_shutdown())

    except *Exception as egroup:
        for exception in egroup.exceptions:
            for line in HABApp.core.lib.exceptions.format_exception(exception):
                log.error(line)
                print(exception)
    else:
        return 0
    return 1


if __name__ == '__main__':

    loop_factory = asyncio.SelectorEventLoop

    # we can have subprocesses (https://docs.python.org/3/library/asyncio-platforms.html#subprocess-support-on-windows)
    # or mqtt support (https://github.com/sbtinstruments/aiomqtt#note-for-windows-users)
    # but not both. For testing, it makes sense to use mqtt support as a default
    if sys.platform.lower() == 'win32' or os.name.lower() == 'nt':
        if os.environ.get('HABAPP_NO_MQTT') is not None:
            loop_factory = asyncio.ProactorEventLoop

    sys.exit(asyncio.run(main(), debug=True, loop_factory=loop_factory))
