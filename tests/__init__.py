import unittest
from inspect import isabstract
from functools import wraps
from typing import Callable


def patches(cls: type, target: str=None, rename_as: str=None, external_decorator: Callable=None):
    def decorator(patch_function: Callable) -> Callable:
        attr_name = target or patch_function.__name__
        original = getattr(cls, attr_name)

        @wraps(patch_function)
        def wrapper(*args, **kwargs):
            return patch_function(*args, **kwargs)
        if external_decorator is not None:
            wrapper = external_decorator(wrapper)
        setattr(cls, attr_name, wrapper)
        if rename_as is not None:
            setattr(cls, rename_as, original)
        return wrapper
    return decorator


@patches(unittest.TestLoader,
         target='loadTestsFromTestCase',
         rename_as='unpatched_loadTestsFromTestCase')
def _loader(self, cls: type):
    # Forces unittest.TestLoader to return tests from abstract base classes as None.
    if isabstract(cls):
        return None
    else:
        return self.unpatched_loadTestsFromTestCase(cls)


@patches(unittest.BaseTestSuite,
         target='__init__',
         rename_as='unpatched_init')
def _initializer(self, tests=()):
    # Forces unittest.BaseTestSuite to filter out missing test classes in its initializer.
    self.unpatched_init(list(filter(lambda x: x is not None, tests)))