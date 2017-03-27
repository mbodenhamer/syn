from .base import SyntagmathonNode, Variable
from .interpreter import eval
from syn.base.b import Attr
from syn.type.a import List
from syn.five import STR

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
        for expr in self.body:
            out = eval(expr, env, **kwargs)
        return out

    def eval(self, env, **kwargs):
        env[self.name] = self
        return self.name


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


#-------------------------------------------------------------------------------
# SpecialCall


class SpecialCall(Call):
    def eval(self, env, **kwargs):
        ret = self.func.call(env, self.args, **kwargs)
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Function', 'Call', 'Special', 'SpecialCall')

#-------------------------------------------------------------------------------
