import operator as op
from .base import Variable
from .function import Function, Special
from syn.base.b import Attr
from syn.type.a import Callable

#-------------------------------------------------------------------------------
# BuiltinFunction


class BuiltinFunction(Function):
    _attrs = dict(body = Attr(Callable))

    def call(self, env, **kwargs):
        args = [env[arg] for arg in self.signature]
        value = self.body(*args)
        return value


#-------------------------------------------------------------------------------
# SpecialForm


class SpecialForm(Special):
    _attrs = dict(body = Attr(Callable))

    def call(self, env, args_, **kwargs):
        args = [args_[arg] for arg in self.signature]
        return self.body(env, *args)
    

#-------------------------------------------------------------------------------
# Utilities

def set_variable(env, name, value):
    if isinstance(name, Variable):
        name = name.name
    env[name] = value
    return name

#-------------------------------------------------------------------------------
# Builtins

Add = BuiltinFunction('Add', ['a', 'b'], op.add)
Sub = BuiltinFunction('Sub', ['a', 'b'], op.sub)
Mul = BuiltinFunction('Mul', ['a', 'b'], op.mul)

Set = SpecialForm('Set', ['name', 'value'], set_variable)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('BuiltinFunction',
           'Add', 'Sub', 'Mul',
           'Set')

#-------------------------------------------------------------------------------
