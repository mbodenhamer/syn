from .base import SyntagmathonNode, Variable
from .interpreter import eval
from .compiler import to_python
from syn.base_utils import pyversion
from syn.base.b import Attr
from syn.type.a import List
from syn.five import STR

VER = pyversion()

#-------------------------------------------------------------------------------
# Function


class Function(SyntagmathonNode):
    _attrs = dict(name = Attr(STR),
                  signature = Attr(List(Variable)),
                  body = Attr(List(SyntagmathonNode)))
    _opts = dict(args = ('name', 'signature', 'body'))

    def __call__(self, *args_, **kwargs):
        args = {}
        for k, arg in enumerate(args_):
            args[self.signature[k].name] = arg

        for key, value in kwargs.items():
            if key in args:
                raise TypeError("Parameter {} specified twice".format(key))
            args[key] = value

        return Call(self, args)

    def call(self, env, **kwargs):
        return eval(self.body, env, **kwargs)

    def eval(self, env, **kwargs):
        env[self.name] = self
        return self.name

    def to_python(self, env, **kwargs):
        from syn.python.b import Arguments, FunctionDef, Return, Pass

        if VER < '3':
            args = Arguments([to_python(arg, env, **kwargs) 
                              for arg in self.signature])
        else:
            from syn.python.b import Arg
            args = Arguments([Arg(arg.name)
                              for arg in self.signature])

        body = to_python(self.body, env, **kwargs)
        if not body:
            body = [Pass()]
        elif not isinstance(self.body[-1], Special):
            body[-1] = Return(body[-1])
        return FunctionDef(self.name, args, body)


#-------------------------------------------------------------------------------
# Special


class Special(Function):
    def __call__(self, *args, **kwargs):
        ret = super(Special, self).__call__(*args, **kwargs)
        return SpecialCall(ret.func, ret.args)


#-------------------------------------------------------------------------------
# Call


class Call(SyntagmathonNode):
    _attrs = dict(func = Attr(Function),
                  args = Attr(dict))
    _opts = dict(args = ('func', 'args'))

    def eval(self, env, **kwargs):
        args = {name: eval(value, env, **kwargs) 
                for name, value in self.args.items()}
        env.push(args)
        ret = self.func.call(env, **kwargs)
        env.pop()
        return ret

    def to_python(self, env, **kwargs):
        from syn.python.b import Call, Name
        args = [to_python(self.args[arg.name], env, **kwargs)
                for arg in self.func.signature]
        if hasattr(self.func, 'python'):
            return self.func.python(env, *args)
        func = Name(self.func.name)
        return Call(func, args)


#-------------------------------------------------------------------------------
# SpecialCall


class SpecialCall(Call):
    def eval(self, env, **kwargs):
        ret = self.func.call(env, self.args, **kwargs)
        return ret

    def to_python(self, env, **kwargs):
        args = [to_python(self.args[arg.name], env, **kwargs)
                for arg in self.func.signature]
        return self.func.python(env, *args)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Function', 'Call', 'Special', 'SpecialCall')

#-------------------------------------------------------------------------------
