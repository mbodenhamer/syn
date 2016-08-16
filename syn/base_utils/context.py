import os
import threading
from syn.five import STR
from contextlib import contextmanager

#-------------------------------------------------------------------------------
# Temporary assignment

@contextmanager
def assign(A, attr, B):
    '''Assigns B to A.attr, yields, and then assigns A.attr back to its original value.'''
    with threading.Lock():
        tmp = getattr(A, attr)
        setattr(A, attr, B)
        yield
        setattr(A, attr, tmp)

#-------------------------------------------------------------------------------
# cd

@contextmanager
def chdir(path):
    with threading.Lock():
        pwd = os.getcwd()
        os.chdir(path)
        yield
        os.chdir(pwd)

#-------------------------------------------------------------------------------
# dels

@contextmanager
def delete(*args):
    '''For using then deleting objects.'''
    from syn.base_utils import this_module
    mod = this_module(npop=3)
    yield
    for arg in args:
        name = arg
        if not isinstance(name, STR):
            name = arg.__name__
        delattr(mod, name)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('assign', 'chdir', 'delete')

#-------------------------------------------------------------------------------
