import os
import threading
from syn.five import STR
from contextlib import contextmanager

#-------------------------------------------------------------------------------
# null_context

@contextmanager
def null_context():
    '''A context manager that does nothing.
    '''
    yield

#-------------------------------------------------------------------------------
# Temporary assignment

@contextmanager
def assign(A, attr, B, lock=False):
    '''Assigns B to A.attr, yields, and then assigns A.attr back to its
    original value.
    '''
    class NoAttr(object): pass

    context = threading.Lock if lock else null_context
    with context():
        if not hasattr(A, attr):
            tmp = NoAttr
        else:
            tmp = getattr(A, attr)

        setattr(A, attr, B)
        yield

        if tmp is NoAttr:
            delattr(A, attr)
        else:
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

__all__ = ('null_context', 'assign', 'chdir', 'delete')

#-------------------------------------------------------------------------------
