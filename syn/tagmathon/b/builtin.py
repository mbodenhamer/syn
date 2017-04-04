import operator as op
from .base import vars
from .function import Function, Special
from .interpreter import eval
from syn.base.b import Attr
from syn.type.a import Callable

#-------------------------------------------------------------------------------
# BuiltinFunction


class BuiltinFunction(Function):
    _attrs = dict(body = Attr(Callable),
                  python = Attr(Callable),
                  pass_kwargs = Attr(bool, False))

    def call(self, env, **kwargs):
        args = [env[arg.name] for arg in self.signature]
        if self.pass_kwargs:
            return self.body(*args, **kwargs)
        return self.body(*args)
        

#-------------------------------------------------------------------------------
# SpecialForm


class SpecialForm(Special):
    _attrs = dict(body = Attr(Callable),
                  python = Attr(Callable))

    def call(self, env, args_, **kwargs):
        args = [args_[arg.name] for arg in self.signature]
        return self.body(env, *args, **kwargs)


#-------------------------------------------------------------------------------
# Builtin Functions

def _assert(a, **kwargs):
    assert a

#-------------------------------------------------------------------------------
# Special Form Functions

def _set_variable(env, name, value, **kwargs):
    name = name.name
    value = eval(value, env, **kwargs)
    env[name] = value
    return value

def _if(env, test, body, orelse, **kwargs):
    if eval(test, env):
        return eval(body, env, **kwargs)
    return eval(orelse, env, **kwargs)

#-------------------------------------------------------------------------------
# Builtin python compilers

def _py_add(a, b, **kwargs):
    from syn.python.b import BinOp, Add
    return BinOp(a, Add(), b)

def _py_sub(a, b, **kwargs):
    from syn.python.b import BinOp, Sub
    return BinOp(a, Sub(), b)

def _py_mul(a, b, **kwargs):
    from syn.python.b import BinOp, Mult
    return BinOp(a, Mult(), b)

def _py_le(a, b, **kwargs):
    from syn.python.b import Compare, LtE
    return Compare(a, [LtE()], [b])

def _py_eq(a, b, **kwargs):
    from syn.python.b import Compare, Eq
    return Compare(a, [Eq()], [b])

def _py_assert(a, **kwargs):
    raise NotImplementedError

def _py_set_variable(name, value, **kwargs):
    from syn.python.b import Assign
    return Assign([name], value)

def _py_if(test, body, orelse, **kwargs):
    from syn.python.b import If
    if not isinstance(body, list):
        body = [body]
    if not isinstance(orelse, list):
        orelse = [orelse]
    return If(test, body, orelse)

#-------------------------------------------------------------------------------
# Builtins

a, b = vars('a', 'b')

Add = BuiltinFunction('add', [a, b], op.add, python=_py_add)
Sub = BuiltinFunction('sub', [a, b], op.sub, python=_py_sub)
Mul = BuiltinFunction('mul', [a, b], op.mul, python=_py_mul)
LE = BuiltinFunction('le', [a, b], op.le, python=_py_le)
Eq = BuiltinFunction('eq', [a, b], op.eq, python=_py_eq)
Assert = BuiltinFunction('assert', [a], _assert, python=_py_assert, 
                         pass_kwargs=True)

Set = SpecialForm('set', list(vars('name', 'value')), _set_variable,
                  python=_py_set_variable)
If = SpecialForm('if', list(vars('test', 'body', 'orelse')), _if,
                 python=_py_if)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('BuiltinFunction',
           'Add', 'Sub', 'Mul', 'LE', 'Eq', 'Assert',
           'Set', 'If')

#-------------------------------------------------------------------------------
