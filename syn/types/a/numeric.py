from six import PY2
from syn.base_utils import setitem, rand_int, rand_float, rand_bool, \
    rand_complex, rand_long
from .base import Type, SER_KEYS
from .ne import NotEqual

#-------------------------------------------------------------------------------
# Utilities

def bool_enumval(x, **kwargs):
    return bool(x % 2)

def float_enumval(x, **kwargs):
    float_step = kwargs.get('float_step', .1)
    return x * float_step

def complex_enumval(x, **kwargs):
    real_step = kwargs.get('real_step', .1)
    imag_step = kwargs.get('imag_step', .05)
    
    new_kwargs = dict(kwargs)
    new_kwargs['float_step'] = real_step
    real = float_enumval(x, **new_kwargs) 

    new_kwargs['float_step'] = imag_step
    imag = float_enumval(x, **new_kwargs) 
    return complex(real, imag)

#-------------------------------------------------------------------------------
# Numeric


class Numeric(Type):
    def estr(self, **kwargs):
        return str(self.obj)

    def _find_ne(self, other, func, **kwargs):
        return NotEqual(self.obj, other)

    def _visit(self, k, **kwargs):
        return self.obj

    def _visit_len(self, **kwargs):
        return 1


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
# Long


class Long(Numeric):
    if PY2:
        type = long

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return long(x)

    def estr(self, **kwargs):
        return repr(self.obj)

    @classmethod
    def _generate(cls, **kwargs):
        return rand_long(**kwargs)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [repr(self.obj)]


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

__all__ = ('Numeric', 'Bool', 'Int', 'Long', 'Float', 'Complex')

#-------------------------------------------------------------------------------
