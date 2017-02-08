from __future__ import division
import sys
import math
from functools import reduce
import operator as op

#-------------------------------------------------------------------------------

# An attempt at a reasonable machine-independent value
DEFAULT_TOLERANCE = math.pow(10, math.log(sys.float_info.epsilon, 10) / 2.0)

#-------------------------------------------------------------------------------
# Comparison

def feq(a, b, tol=DEFAULT_TOLERANCE, relative=False):
    from syn.five import NUM
    if isinstance(a, NUM) and isinstance(b, NUM):
        ret = abs(abs(a) - abs(b)) < tol
        if relative and not ret and a != 0 and b != 0:
            M = min(abs(a), abs(b))
            A = a / M
            B = b / M
            ret = abs(abs(A) - abs(B)) < tol
        return ret
    return a == b

def cfeq(a, b, tol=DEFAULT_TOLERANCE, relative=False):
    if isinstance(a, complex) and isinstance(b, complex):
        return (feq(a.real, b.real, tol, relative) and 
                feq(a.imag, b.imag, tol, relative))
    return feq(a, b, tol, relative)

#-------------------------------------------------------------------------------
# Math

def prod(args, log=False):
    if log:
        tmp = sum(math.log(arg) for arg in args)
        return math.exp(tmp)

    return reduce(op.mul, args)

def sgn(x):
    if x == 0:
        return 0
    elif x < 0:
        return -1
    return 1

#-------------------------------------------------------------------------------
# __all__

__all__ = ('feq', 'cfeq', 'prod', 'sgn')

#-------------------------------------------------------------------------------
