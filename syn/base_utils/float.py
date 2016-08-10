import sys
import math
from syn.five import NUM

#-------------------------------------------------------------------------------

DEFAULT_TOLERANCE = math.pow(10, math.log(sys.float_info.epsilon, 10) / 2.0)

#-------------------------------------------------------------------------------
# Comparison

def feq(a, b, tol=DEFAULT_TOLERANCE):
    if isinstance(a, NUM) and isinstance(b, NUM):
        ret = abs(abs(a) - abs(b)) < tol
        return ret
    return a == b

#-------------------------------------------------------------------------------
# __all__

__all__ = ('feq',)

#-------------------------------------------------------------------------------
