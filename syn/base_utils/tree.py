#-------------------------------------------------------------------------------
# seq_list_nested

def seq_list_nested(b, d, x=0, top_level=True):
    '''
    Create a nested list of iteratively increasing values.

    b: branching factor
    d: max depth
    x: starting value (default = 0)
    '''
    x += 1

    if d == 0:
        ret = [x]
    else:
        val = x
        ret = []
        for i in range(b):
            lst, x = seq_list_nested(b, d-1, x, False)
            ret.extend(lst)
        ret = [val, ret]
            
    if top_level:
        return ret
    else:
        return ret, x

#-------------------------------------------------------------------------------
# __all__

__all__ = ('seq_list_nested',)

#-------------------------------------------------------------------------------
