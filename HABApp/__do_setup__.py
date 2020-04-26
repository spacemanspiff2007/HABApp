# -----------------------------------------------------------------------------
# setup astral
# -----------------------------------------------------------------------------
import astral
astral._LOCATION_INFO = ''  # Remove City list because we don't need it and it is rather big

# -----------------------------------------------------------------------------
# setup pydantic
# -----------------------------------------------------------------------------
import pydantic  # noqa: E402

pydantic.BaseConfig.extra = pydantic.Extra.forbid           # Don't allow extra keys
pydantic.BaseConfig.allow_population_by_field_name = True   # Allow setting value by key name

# -----------------------------------------------------------------------------
# if installed we use uvloop because it seems to be much faster (untested)
# -----------------------------------------------------------------------------
try:
    import uvloop   # type: ignore

    uvloop.install()
    print('Using uvloop')
except ModuleNotFoundError:
    pass
