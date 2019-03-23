import functools
import traceback


def PrintException( func):

    @functools.wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("{}\n{}".format( e, traceback.format_exc()))
            raise
    return f
