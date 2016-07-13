import threading
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
# __all__

__all__ = ('assign',)

#-------------------------------------------------------------------------------
