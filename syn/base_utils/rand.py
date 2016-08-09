'''Random value-generating utilities.  Intended mainly for generating random values for testing purposes (i.e. finding edge cases).
'''

import sys
from random import randint, random
from syn.five import unichr, xrange, PY2

#-------------------------------------------------------------------------------

MAX_INT = sys.maxsize
MIN_INT = -MAX_INT - 1

MIN_CHR = 0x00
MAX_CHR = 0xff
MIN_UNICHR = 0x00
MAX_UNICHR = sys.maxunicode
MIN_STRLEN = 0
MAX_STRLEN = 100
MAX_FLOAT = sys.float_info.max
MIN_FLOAT = -MAX_FLOAT

inf = float('inf')

#-------------------------------------------------------------------------------
# Numeric

def rand_bool(thresh=0.5):
    if random() > thresh:
        return True
    return False

def rand_int(min_val = MIN_INT, max_val = MAX_INT):
    return randint(min_val, max_val)

def rand_long(min_len=None, max_len=None):
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

def rand_float(lb = None, ub = None):
    if lb is not None and ub is not None:
        return (ub - lb) * random() + lb
    elif ub is not None:
        m = ub
    else:
        m = MAX_FLOAT

    sign = 1 if rand_bool() else -1
    return sign * m * random()

def rand_complex(imag_only=False):
    real = 0
    if not imag_only:
        real = rand_float()
    imag = rand_float()
    return complex(real, imag)
 
#-------------------------------------------------------------------------------
# String

def rand_str(min_char=MIN_CHR, max_char=MAX_CHR, min_len=MIN_STRLEN, 
             max_len=MAX_STRLEN, func=chr):
    '''For values in the (extended) ASCII range, regardless of Python version.
    '''
    l = randint(min_len, max_len)

    ret = ''
    for k in xrange(l):
        ret += func(randint(min_char, max_char))
    return ret

def rand_unicode(min_char=MIN_UNICHR, max_char=MAX_UNICHR, min_len=MIN_STRLEN,
                 max_len=MAX_STRLEN):
    '''For values in the unicode range, regardless of Python version.
    '''
    return rand_str(min_char, max_char, min_len, max_len, unichr)

#-------------------------------------------------------------------------------
# Misc.

def rand_none():
    return None

#-------------------------------------------------------------------------------
# Dispatch

GENERATORS = {bool: rand_bool,
              int: rand_int,
              float: rand_float,
              complex: rand_complex,
              str: rand_str,
              type(None): rand_none}

if PY2:
    GENERATORS[long] = rand_long
    GENERATORS[unicode] = rand_unicode

def rand_dispatch(typ, *args, **kwargs):
    if typ in GENERATORS:
        return GENERATORS[typ](*args, **kwargs)
    raise TypeError('Cannot dispatch random generator for type: {}'.
                    format(typ))

#-------------------------------------------------------------------------------
# __all__

__all__ = ('rand_bool', 'rand_int', 'rand_float', 'rand_complex', 'rand_long',
           'rand_str', 'rand_unicode',
           'rand_none',
           'rand_dispatch')

#-------------------------------------------------------------------------------
