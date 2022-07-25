from HABApp.__check_dependency_packages__ import check_dependency_packages

# -----------------------------------------------------------------------------
# if installed we use uvloop because it seems to be much faster (untested)
# -----------------------------------------------------------------------------
try:
    import uvloop   # type: ignore

    uvloop.install()
    print('Using uvloop')
except ModuleNotFoundError:
    pass


# -----------------------------------------------------------------------------
# Check that all dependencies are installed
# We do this here, so we can print a nice error message. Otherwise the corresponding
# module import will fail somewhere in the middle of the startup process
# -----------------------------------------------------------------------------
check_dependency_packages()
