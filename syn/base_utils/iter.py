from itertools import islice
from collections import Iterator

#-------------------------------------------------------------------------------

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

def consume(iter, N=None):
    '''Consumes N items from iter.  If N is None (or not given), consumes all.
    '''
    if N is None:
        list(iter)
    else:
        list(islice(iter, N))

#-------------------------------------------------------------------------------
# __all__

__all__ = ('consume', 'iterlen', 'is_empty')

#-------------------------------------------------------------------------------
