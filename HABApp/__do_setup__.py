# setup used libraries

import astral   # type: ignore

# Remove City list because we don't need it
astral._LOCATION_INFO = ''


# if installed we use uvloop because it seems to be much faster (untested)
try:
    import uvloop   # type: ignore

    uvloop.install()
    print('Using uvloop')
except ModuleNotFoundError:
    pass
