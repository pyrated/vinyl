import unittest
from inspect import isabstract
from functools import wraps
from typing import Callable, Tuple, Any


__all__ = [
    'unittest'
]


def patches(cls: type, target: str=None, rename_to: str=None, external_decorator: Callable[[Any], Any]=None):
    def decorator(patch_function: Callable[[Any], Any]) -> Callable:
        attr_name = target or patch_function.__name__
        original = getattr(cls, attr_name)

        @wraps(patch_function)
        def wrapper(*args, **kwargs):
            return patch_function(*args, **kwargs)
        if external_decorator is not None:
            wrapper = external_decorator(wrapper)
        setattr(cls, attr_name, wrapper)
        if rename_to is not None:
            setattr(cls, rename_to, original)
        return wrapper
    return decorator


@patches(unittest.TestLoader,
         target='loadTestsFromTestCase',
         rename_to='unpatched_loadTestsFromTestCase')
def _loader(self, cls: type):
    # Forces unittest.TestLoader to return tests from abstract base classes as None.
    if isabstract(cls):
        return None
    else:
        return self.unpatched_loadTestsFromTestCase(cls)


@patches(unittest.BaseTestSuite,
         target='__init__',
         rename_to='unpatched_init')
def _initializer(self, tests: Tuple[type]=()):
    # Forces unittest.BaseTestSuite to filter out missing test classes in its initializer.
    self.unpatched_init(list(filter(lambda x: x is not None, tests)))