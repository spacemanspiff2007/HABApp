from typing import Final, Optional, Callable, Any

from HABApp.openhab.connection_logic.plugin_things.cfg_validator import UserItem
from .formatter import TYPE_FORMATTER, EmptyFormatter, ValueFormatter


class BuilderBase:
    def create_formatter(self, item_obj: UserItem) -> 'TYPE_FORMATTER':
        raise NotImplementedError()


class ConstValueFormatterBuilder(BuilderBase):
    def __init__(self, value: str, condition: Optional[Callable] = None):
        self.value: Final = value
        self.condition: Final = condition

    def create_formatter(self, item_obj: UserItem) -> 'TYPE_FORMATTER':
        if self.condition is None or self.condition(item_obj):
            return ValueFormatter(self.value)
        return EmptyFormatter()


class ValueFormatterBuilder(BuilderBase):
    def __init__(self, name: str, fmt_value: str):
        self.name: Final = name
        self.fmt_value: Final = fmt_value

    def get_value(self, item_obj: UserItem):
        return getattr(item_obj, self.name)

    def create_formatter(self, item_obj: UserItem) -> 'TYPE_FORMATTER':
        value = self.get_value(item_obj)
        if not isinstance(value, str):
            raise ValueError('Expected str!')

        value = value.strip()
        if not value:
            return EmptyFormatter()
        return ValueFormatter(self.fmt_value.format(value))


class MultipleValueFormatterBuilder(ValueFormatterBuilder):

    def __init__(self, name: str, fmt_value: str, wrapped_by: str):
        super().__init__(name, fmt_value)
        self.wrapped_by: Final = wrapped_by

    def create_formatter(self, item_obj: UserItem) -> 'TYPE_FORMATTER':
        values = self.get_value(item_obj)
        if not isinstance(values, (list, set, tuple, frozenset)):
            raise ValueError('Expected container!')

        values = map(lambda x: x.strip(), values)

        # remove all empty str and sort
        values = sorted(filter(None, values))
        if not values:
            return EmptyFormatter()

        value = ', '.join(map(self.fmt_value.format, values))
        return ValueFormatter(self.wrapped_by.format(value))


class LinkFormatter(BuilderBase):

    def create_formatter(self, item_obj: UserItem) -> 'TYPE_FORMATTER':
        link = item_obj.link.strip()
        if not link:
            return EmptyFormatter()

        value = f'channel = "{link:s}"'
        if item_obj.metadata:
            value += ','

        return ValueFormatter(value)


def metadata_key_value(key: str, value: Any):
    return f'{key}={value}' if not isinstance(value, str) else f'{key}="{value}"'


class MetadataFormatter(BuilderBase):

    def create_formatter(self, item_obj: UserItem) -> 'TYPE_FORMATTER':
        metdata = item_obj.metadata
        if not metdata:
            return EmptyFormatter()

        strs = []
        for name, __meta in sorted(metdata.items(), key=lambda x: x[0]):
            value = __meta['value']
            config = __meta['config']

            # a=1 or a="test"
            metadata_str = metadata_key_value(name, value)
            if config:
                config_strs = []
                for config_key, config_value in sorted(config.items(), key=lambda x: x[0]):
                    config_strs.append(metadata_key_value(config_key, config_value))

                metadata_str += f' [{", ".join(config_strs)}]'

            strs.append(metadata_str)

        return ValueFormatter(', '.join(strs))
