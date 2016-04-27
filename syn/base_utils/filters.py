'''Various filters for processing arguments.  Inteded for use in the call keyword argument to the base.Base constructor.
'''

#-------------------------------------------------------------------------------
# String

def split(obj, sep=None):
    if sep is None:
        return obj.split()
    return obj.split(sep)

#-------------------------------------------------------------------------------
# Sequence

def join(obj, sep=' '):
    return sep.join(obj)

def dictify_strings(obj, empty=None, sep=None):
    if empty is None and sep is not None:
        empty = False
    elif empty is None:
        empty = True
    
    ret = {}
    for s in obj:
        if empty:
            name = s
            val = ''
        else:
            name, val = split(s, sep)
        ret[name.strip()] = val.strip()
    return ret

#-------------------------------------------------------------------------------
# __all__

__all__ = ('split', 'join', 'dictify_strings')

#-------------------------------------------------------------------------------
