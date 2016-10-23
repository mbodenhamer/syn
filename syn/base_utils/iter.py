import math
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
# Query

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
    for x in iter:
        pass
    return x

#-------------------------------------------------------------------------------
# Calculation

def iteration_length(N, start=0, step=1):
    '''Return the number of iteration steps over a list of length N,
starting at index start, proceeding step elements at a time.
    '''
    if N < 0:
        raise ValueError('N cannot be negative')

    if start < 0:
        start += N
        if start < 0:
            raise ValueError('Invalid start value')

    if step < 0:
        step = -step
        new_N = start + 1
        if new_N > N:
            raise ValueError('Invalid parameters')
        N = new_N
        start = 0

    ret = int(math.ceil((N - start) / float(step)))
    return max(0, ret)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('iterlen', 'is_empty', 'consume', 'first', 'last',
           'iteration_length')

#-------------------------------------------------------------------------------
