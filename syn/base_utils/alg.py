'''Some general purpose algorithms.'''

from .list import indices_removed

#-------------------------------------------------------------------------------
# defer_reduce

def defer_reduce(func, items, test, accum=None):
    '''Recursively reduce items by func, but only the items that do not cause test(items, accum) to return False.  Returns the reduced list (accum) and the list of remaining deferred items.
    '''
    removals = []

    for k, item in enumerate(items):
        if test(item, accum):
            removals.append(k)
            if accum is None:
                accum = item
            else:
                accum = func(accum, item)
        
    deferred = indices_removed(items, removals)
    
    if deferred == items or not deferred:
        return accum, deferred

    return defer_reduce(func, deferred, test, accum)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('defer_reduce',)

#-------------------------------------------------------------------------------
