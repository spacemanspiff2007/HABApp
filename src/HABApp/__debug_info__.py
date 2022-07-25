import platform
import sys
from HABApp.__version__ import __version__


def get_debug_info() -> str:

    info = {
        'HABApp': __version__,
        'Platform': platform.platform(),
        'Machine': platform.machine(),
        'Python': sys.version,
    }

    indent = max(map(lambda x: len(x), info))
    ret = '\n'.join('{:{indent}s}: {:s}'.format(k, str(v).replace('\n', ''), indent=indent) for k, v in info.items())

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
