from pydantic import BaseModel, Extra, validator


class RestBase(BaseModel):

    # default configuration for RestAPI models
    class Config:
        extra = Extra.forbid


def none_is_empty_str(v) -> str:
    return None if v == 'NONE' else v


def make_none_empty_str(*name: str):
    return validator(*name, allow_reuse=True)(none_is_empty_str)
