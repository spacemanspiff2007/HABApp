from typing import Any

from pydantic.fields import Field


# todo: move this to easyconfig
def EasyConfigField(*args, in_file: bool = True, **kwargs) -> Any:
    """Custom pydantic.Field that adds 'in_file' to json_schema_extra.

    The `in_file` parameter is used by easyconfig to skip entries from appearing in the default file.

    :param args: Positional arguments for the pydantic.Field constructor.
    :param in_file: Boolean that defines whether the field should be visible in the default file.
    :param kwargs: Keyword arguments for the pydantic.Field constructor.
    """
    field = Field(*args, **kwargs)
    if isinstance(field.json_schema_extra, dict):
        field.json_schema_extra['in_file'] = in_file
    else:
        field.json_schema_extra = {'in_file': in_file}
    return field