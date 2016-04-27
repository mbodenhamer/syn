'''Various filters for processing arguments.  Inteded for use in the call keyword argument to the base.Base constructor.
'''

from syn.five import STR
from collections import Sequence, Mapping

#-------------------------------------------------------------------------------
# String

def split(obj, sep=None):
    if isinstance(obj, STR) or not isinstance(obj, Sequence):
        if sep is None:
            return obj.split()
        return obj.split(sep)
    return obj

#-------------------------------------------------------------------------------
# Sequence

def join(obj, sep=' '):
    if isinstance(obj, Sequence) and not isinstance(obj, STR):
        return sep.join(obj)
    return obj

def dictify_strings(obj, empty=None, sep=None, typ=dict):
    if not isinstance(obj, Mapping):
        if empty is None and sep is not None:
            empty = False
        elif empty is None:
            empty = True

        ret = typ()
        for s in obj:
            if empty:
                name = s
                val = ''
            else:
                name, val = split(s, sep)
            ret[name.strip()] = val.strip()
        return ret
    return typ(obj)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('split', 'join', 'dictify_strings')

#-------------------------------------------------------------------------------
