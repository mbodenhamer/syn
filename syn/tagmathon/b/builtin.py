import operator as op
from .base import Variable, vars
from .function import Function, Special
from .interpreter import eval
from syn.base.b import Attr
from syn.type.a import Callable

#-------------------------------------------------------------------------------
# BuiltinFunction


class BuiltinFunction(Function):
    _attrs = dict(body = Attr(Callable))

    def call(self, env, **kwargs):
        args = [env[arg.name] for arg in self.signature]
        value = self.body(*args)
        return value


#-------------------------------------------------------------------------------
# SpecialForm


class SpecialForm(Special):
    _attrs = dict(body = Attr(Callable))

    def call(self, env, args_, **kwargs):
        args = [args_[arg.name] for arg in self.signature]
        return self.body(env, *args)
    

#-------------------------------------------------------------------------------
# Special Form Functions

def set_variable(env, name, value):
    if isinstance(name, Variable):
        name = name.name
    env[name] = eval(value, env)
    return name

def if_(env, test, body, orelse):
    if eval(test, env):
        return eval(body, env)
    return eval(orelse, env)

#-------------------------------------------------------------------------------
# Builtins

a, b = vars('a', 'b')

Add = BuiltinFunction('Add', [a, b], op.add)
Sub = BuiltinFunction('Sub', [a, b], op.sub)
Mul = BuiltinFunction('Mul', [a, b], op.mul)

Set = SpecialForm('Set', list(vars('name', 'value')), set_variable)
If = SpecialForm('If', list(vars('test', 'body', 'orelse')), if_)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('BuiltinFunction',
           'Add', 'Sub', 'Mul',
           'Set', 'If')

#-------------------------------------------------------------------------------
