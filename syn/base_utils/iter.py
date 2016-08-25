def consume(iter, N=None):
    from itertools import islice
    if N is None:
        list(iter)
    else:
        list(islice(iter, N))

#-------------------------------------------------------------------------------
# __all__

__all__ = ('consume',)

#-------------------------------------------------------------------------------
