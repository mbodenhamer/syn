import sys
import math
from syn.five import NUM

#-------------------------------------------------------------------------------

# An attempt at a reasonable machine-independent value
DEFAULT_TOLERANCE = math.pow(10, math.log(sys.float_info.epsilon, 10) / 2.0)

#-------------------------------------------------------------------------------
# Comparison

def feq(a, b, tol=DEFAULT_TOLERANCE):
    if isinstance(a, NUM) and isinstance(b, NUM):
        ret = abs(abs(a) - abs(b)) < tol
        return ret
    return a == b

#-------------------------------------------------------------------------------
# Math

def prod(args, log=False):
    if log:
        tmp = sum(math.log(arg) for arg in args)
        return math.exp(tmp)

    ret = 1
    lst = list(args)
    while lst:
        ret *= lst.pop()
    return ret

#-------------------------------------------------------------------------------
# __all__

__all__ = ('feq', 'prod')

#-------------------------------------------------------------------------------
