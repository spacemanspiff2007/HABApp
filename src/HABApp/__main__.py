import asyncio
import logging
import signal
import sys
import traceback
import typing


def get_debug_info() -> str:
    import platform
    import sys

    info = {
        'Platform': platform.platform(),
        'Machine': platform.machine(),
        'Python version': sys.version,
    }

    ret = '\n'.join('{:20s}: {:s}'.format(k, str(v).replace('\n', '')) for k, v in info.items())

    try:
        import pkg_resources
        installed_packages = {p.key: p.version for p in sorted(pkg_resources.working_set, key=lambda x: x.key)}

        indent = max(map(len, installed_packages.keys()), default=1) + 2
        table = '\n'.join(f'{k:{indent}s}: {v}' for k, v in installed_packages.items())

        if installed_packages:
            ret += f'\n\nInstalled Packages\n{"-" * 80}\n{table}'

    except Exception as e:
        ret += f'\n\nCould not get installed Packages!\nError: {str(e)}'

    return ret


def print_debug_info():
    print(f'Debug information\n{"-" * 80}')
    print(get_debug_info())


try:
    import HABApp
    from HABApp.__cmd_args__ import parse_args, find_config_folder
    from HABApp.__splash_screen__ import show_screen
except (ModuleNotFoundError, ImportError) as dep_err:
    print(f'Error!\nDependency "{dep_err.name}" is missing!\n\n')
    print_debug_info()
    sys.exit(100)


def register_signal_handler():
    def shutdown_handler(sig, frame):
        print('Shutting down ...')
        HABApp.runtime.shutdown.request_shutdown()

    # register shutdown helper
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def main() -> typing.Union[int, str]:

    show_screen()

    # This has do be done before we create HABApp because of the possible sleep time
    args = parse_args()

    if HABApp.__cmd_args__.DO_DEBUG:
        print_debug_info()
        sys.exit(0)

    log = logging.getLogger('HABApp')

    cfg_folder = find_config_folder(args.config)

    try:
        app = HABApp.runtime.Runtime()
        register_signal_handler()

        # start workers
        try:
            asyncio.ensure_future(app.start(cfg_folder))
            HABApp.core.const.loop.run_forever()
        except asyncio.CancelledError:
            pass

    except HABApp.config.InvalidConfigException:
        pass
    except Exception as e:
        for line in traceback.format_exc().splitlines():
            log.error(line)
            print(e)
        return str(e)
    finally:
        # Sleep to allow underlying connections of aiohttp to close
        # https://aiohttp.readthedocs.io/en/stable/client_advanced.html#graceful-shutdown
        HABApp.core.const.loop.run_until_complete(asyncio.sleep(1))
        HABApp.core.const.loop.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
