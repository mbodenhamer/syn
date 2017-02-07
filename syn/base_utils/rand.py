'''Random value-generating utilities.  Intended mainly for generating random values for testing purposes (i.e. finding edge cases).
'''

import sys
from random import randint, random, choice
from six import PY2, PY3

if PY3:
    xrange = range

#-------------------------------------------------------------------------------

MAX_INT = sys.maxsize
MIN_INT = -MAX_INT - 1

MIN_CHR = 0x00
MAX_CHR = 0xff
MIN_UNICHR = 0x00
MAX_UNICHR = sys.maxunicode
MIN_STRLEN = 0
MAX_STRLEN = 10
MAX_FLOAT = sys.float_info.max
MIN_FLOAT = -MAX_FLOAT
MIN_SEQLEN = 0
MAX_SEQLEN = 5
MAX_DEPTH = 1

PRIMITIVE_TYPES = [bool, int, float, complex, str, type(None)]
if PY2:
    PRIMITIVE_TYPES += [long, unicode]
if PY3:
    PRIMITIVE_TYPES += [bytes]

HASHABLE_TYPES = PRIMITIVE_TYPES + [tuple, frozenset]
SEQ_TYPES = PRIMITIVE_TYPES + [list, tuple, dict, set, frozenset]

inf = float('inf')

#-------------------------------------------------------------------------------
# Numeric

def rand_bool(thresh=0.5, **kwargs):
    if random() > thresh:
        return True
    return False

def rand_int(min_val = MIN_INT, max_val = MAX_INT, **kwargs):
    return randint(min_val, max_val)

def rand_long(min_len=None, max_len=None, **kwargs):
    if min_len is None:
        min_len = len(str(MAX_INT)) + 2
    if max_len is None:
        max_len = min_len + 40

    s = rand_str(min_char = ord('0'), max_char = ord('9'), 
                 min_len = min_len, max_len = max_len)

    ret = long(s)
    if rand_bool():
        ret = -ret
    return ret

def rand_float(lb = None, ub = None, **kwargs):
    if lb is not None and ub is not None:
        return (ub - lb) * random() + lb
    elif ub is not None:
        m = ub
    else:
        m = MAX_FLOAT

    sign = 1 if rand_bool() else -1
    return sign * m * random()

def rand_complex(imag_only=False, **kwargs):
    real = 0
    if not imag_only:
        real = rand_float()
    imag = rand_float()
    return complex(real, imag)
 
#-------------------------------------------------------------------------------
# String

def rand_str(min_char=MIN_CHR, max_char=MAX_CHR, min_len=MIN_STRLEN, 
             max_len=MAX_STRLEN, func=chr, **kwargs):
    '''For values in the (extended) ASCII range, regardless of Python version.
    '''
    l = randint(min_len, max_len)

    ret = ''
    for k in xrange(l):
        ret += func(randint(min_char, max_char))
    return ret

def rand_unicode(min_char=MIN_UNICHR, max_char=MAX_UNICHR, min_len=MIN_STRLEN,
                 max_len=MAX_STRLEN, **kwargs):
    '''For values in the unicode range, regardless of Python version.
    '''
    from syn.five import unichr
    return unicode(rand_str(min_char, max_char, min_len, max_len, unichr))

def rand_bytes(**kwargs):
    kwargs['types'] = [int]
    kwargs['min_val'] = 0
    kwargs['max_val'] = 255
    
    values = rand_list(**kwargs)
    return bytes(values)

#-------------------------------------------------------------------------------
# Sequence

def rand_list(**kwargs):
    min_len = kwargs.get('min_len', MIN_SEQLEN)
    max_len = kwargs.get('max_len', MAX_SEQLEN)
    types = kwargs.get('types', SEQ_TYPES)
    depth = kwargs.get('depth', 0)
    max_depth = kwargs.get('max_depth', MAX_DEPTH)

    if depth >= max_depth:
        types = [t for t in types if t in PRIMITIVE_TYPES]

    ret = []
    kwargs['depth'] = depth + 1
    N = randint(min_len, max_len)
    for k in xrange(N):
        typ = choice(types)
        ret.append(rand_dispatch(typ, **kwargs))

    return ret

def rand_tuple(**kwargs):
    return tuple(rand_list(**kwargs))

#-------------------------------------------------------------------------------
# Mapping

def rand_dict(**kwargs):
    key_types = kwargs.get('key_types', HASHABLE_TYPES)
    key_kwargs = dict(kwargs)
    key_kwargs['types'] = key_types

    keys = rand_list(**key_kwargs)
    values = rand_list(**kwargs)
    N = min(len(keys), len(values))
    return dict(zip(keys[:N], values[:N]))

#-------------------------------------------------------------------------------
# Set

def rand_set(**kwargs):
    kwargs['types'] = kwargs.get('types', HASHABLE_TYPES)
    return set(rand_list(**kwargs))

def rand_frozenset(**kwargs):
    return frozenset(rand_set(**kwargs))

#-------------------------------------------------------------------------------
# Misc.

def rand_none(**kwargs):
    return None

#-------------------------------------------------------------------------------
# Dispatch

GENERATORS = {bool: rand_bool,
              int: rand_int,
              float: rand_float,
              complex: rand_complex,
              str: rand_str,
              list: rand_list,
              tuple: rand_tuple,
              dict: rand_dict,
              set: rand_set,
              frozenset: rand_frozenset,
              type(None): rand_none}

if PY2:
    GENERATORS[long] = rand_long
    GENERATORS[unicode] = rand_unicode

if PY3:
    GENERATORS[bytes] = rand_bytes

def rand_dispatch(typ, **kwargs):
    from .py import hasmethod

    if typ in GENERATORS:
        return GENERATORS[typ](**kwargs)
    elif hasmethod(typ, '_generate'):
        return typ._generate(**kwargs)
    raise TypeError('Cannot dispatch random generator for type: {}'.
                    format(typ))

def rand_primitive(**kwargs):
    return rand_dispatch(choice(PRIMITIVE_TYPES), **kwargs)

def rand_hashable(**kwargs):
    kwargs['types'] = HASHABLE_TYPES
    return rand_dispatch(choice(HASHABLE_TYPES), **kwargs)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('rand_bool', 'rand_int', 'rand_float', 'rand_complex', 'rand_long',
           'rand_str', 'rand_unicode', 'rand_bytes',
           'rand_list', 'rand_tuple', 'rand_dict',
           'rand_set', 'rand_frozenset',
           'rand_none',
           'rand_dispatch', 'rand_primitive', 'rand_hashable')

#-------------------------------------------------------------------------------
