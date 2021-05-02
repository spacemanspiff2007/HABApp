from statistics import mean, median
from typing import Union


def format_duration(duration: Union[None, str, float]) -> str:
    if duration is None:
        return ' ' * 6
    if isinstance(duration, str):
        return f'{duration:^6s}'

    if duration < 0.0001:
        # 99.9ns
        return f'{duration * 1000 * 1000:4.1f}us'
    elif duration < 0.01:
        # 9.99ms
        return f'{duration * 1000:4.2f}ms'
    elif duration < 0.1:
        # 99.9ms
        return f'{duration * 1000:4.1f}ms'
    elif duration < 10:
        # 1.234s
        return f'{duration:5.3f}s'
    else:
        #  19.2s
        return f'{duration:5.1f}s'


class BenchContainer:
    def __init__(self):
        self.times = []

    def create(self, name: str) -> 'BenchTime':
        c = BenchTime(name)
        self.times.append(c)
        return c

    def show(self):
        indent = max(map(lambda x: len(x.name), self.times), default=0)
        BenchTime.show_table(indent)
        for b in self.times:
            b.show(indent)
        print('')


class BenchTime:

    @classmethod
    def show_table(cls, indent_name=0):
        print(f'{"":{indent_name}s} | {format_duration("dur")} | {"per sec":7s} | 'f'{format_duration("median")} | '
              f'{format_duration("min")} | {format_duration("max")} | {format_duration("mean")}')

    def __init__(self, name: str, factor: int = 1):
        self.name = name
        self.times = []
        self.factor = factor

    def show(self, indent_name=0):
        total = sum(self.times)
        count = len(self.times)
        _mean = mean(self.times) if self.times else 0
        _medi = median(self.times) if self.times else 0

        per_sec = ((count * self.factor) / total) if total else 0
        unit = ''
        if per_sec > 1000:
            per_sec /= 1000
            unit = 'k'
        if per_sec > 1000:
            per_sec /= 1000
            unit = 'm'

        print(f'{self.name:>{indent_name}s} | {format_duration(total)} | '
              f'{per_sec:{7 - len(unit)}.{3 - len(unit)}f}{unit} | '
              f'{format_duration(_medi)} | {format_duration(min(self.times, default=0))} | '
              f'{format_duration(max(self.times, default=0))} | '
              f'{format_duration(_mean)}')
