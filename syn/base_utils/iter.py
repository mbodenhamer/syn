from functools import wraps
from itertools import islice
from collections import Iterator

#-------------------------------------------------------------------------------
# Utilities

def ensure_iter(f):
    @wraps(f)
    def func(it, *args, **kwargs):
        if not isinstance(it, Iterator):
            it = iter(it)
        return f(it, *args, **kwargs)
    return func

#-------------------------------------------------------------------------------
# Status

def iterlen(iter):
    '''Returns the number of iterations remaining over iter.
    '''
    if not isinstance(iter, Iterator):
        return len(iter)
    return iter.__length_hint__()

def is_empty(iter):
    '''Returns True if iter is empty, otherwise False.
    '''
    return iterlen(iter) == 0

#-------------------------------------------------------------------------------
# Modification

@ensure_iter
def consume(iter, N=None):
    '''Consumes N items from iter.  If N is None (or not given), consumes all.
    '''
    i = iter
    if N is not None:
        i = islice(iter, N)

    for x in i:
        pass

@ensure_iter
def first(iter):
    return next(iter)

@ensure_iter
def last(iter):
    consume(iter, iterlen(iter) - 1)
    return next(iter)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('iterlen', 'is_empty', 'consume', 'first', 'last')

#-------------------------------------------------------------------------------
