from pydantic import BaseModel, Extra


class RestBase(BaseModel):

    # default configuration for RestAPI models
    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True
