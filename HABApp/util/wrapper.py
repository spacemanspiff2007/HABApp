import functools
import logging
import time
import traceback


def PrintException( func):
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("{}\n{}".format( e, traceback.format_exc()))
            raise
    return f


log_worker = logging.getLogger('HABApp.Worker')

def WorkerRuleWrapper(func, rule_instance):

    _class_name = str(type(rule_instance))
    if _class_name.startswith("<class '<run_path>."):
        _class_name = _class_name[19:-2]

    @functools.wraps(func)
    def f(*args, **kwargs):
        __start = time.time()

        try:
            func(*args, **kwargs)
        except Exception as e:
            log_worker.error("{}\n{}".format( e, traceback.format_exc()))

        __dur = time.time() - __start
        if __dur > 0.8:
            log_worker.warning(f'Execution of {_class_name}.{func.__name__} took too long: {__dur:.1f}s')
    return f
