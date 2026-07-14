from pydantic import BaseModel, ConfigDict, validator


class RestBase(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


def none_is_empty_str(v) -> str:
    return None if v == 'NONE' else v


def make_none_empty_str(*name: str):
    return validator(*name, allow_reuse=True)(none_is_empty_str)
