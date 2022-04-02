# HOW TO USE: https://modthesims.info/showthread.php?p=4751246#post4751246

from functools import wraps
import inspect

def inject(target_function, new_function):
    @wraps(target_function)
    def _wrapper_function(*args, **kwargs):
        return new_function(target_function, *args, **kwargs)
    if inspect.ismethod(target_function):
        return classmethod(_wrapper_function)
    else:
        return _wrapper_function

def inject_to(target_object, target_function_name):
    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function
    return _inject_to

def is_injectable(target_function, new_function):
    target_argspec = inspect.getargspec(target_function)
    new_argspec = inspect.getargspec(new_function)
    return len(target_argspec.args) == len(new_argspec.args) - 1
