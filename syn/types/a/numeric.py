from syn.base_utils import setitem, rand_int, rand_float, rand_bool, \
    rand_complex
from .base import Type

#-------------------------------------------------------------------------------
# Utilities

def bool_enumval(x, **kwargs):
    return bool(x % 2)

def float_enumval(x, **kwargs):
    float_step = kwargs.get('float_step', .1)
    return x * float_step

def complex_enumval(x, **kwargs):
    real_step = kwargs.get('real_step', .1)
    imag_step = kwargs.get('real_step', .05)
    
    with setitem(kwargs, 'float_step', real_step):
        real = float_enumval(x, **kwargs) 
    with setitem(kwargs, 'float_step', imag_step):
        imag = float_enumval(x, **kwargs) 
    return complex(real, imag)

#-------------------------------------------------------------------------------
# Numeric


class Numeric(Type):
    def estr(self, **kwargs):
        return str(self.obj)


#-------------------------------------------------------------------------------
# Bool


class Bool(Numeric):
    type = bool

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return bool_enumval(x, **kwargs)

    @classmethod
    def _generate(cls, **kwargs):
        return rand_bool(**kwargs)


#-------------------------------------------------------------------------------
# Int


class Int(Numeric):
    type = int

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return x

    @classmethod
    def _generate(cls, **kwargs):
        return rand_int(**kwargs)


#-------------------------------------------------------------------------------
# Float


class Float(Numeric):
    type = float

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return float_enumval(x, **kwargs)

    @classmethod
    def _generate(cls, **kwargs):
        return rand_float(**kwargs)


#-------------------------------------------------------------------------------
# Complex


class Complex(Numeric):
    type = complex

    ser_args = ('real', 'imag')

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return complex_enumval(x, **kwargs)

    @classmethod
    def _generate(cls, **kwargs):
        return rand_complex(**kwargs)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Numeric', 'Bool', 'Int', 'Float', 'Complex')

#-------------------------------------------------------------------------------
