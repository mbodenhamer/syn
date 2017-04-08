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
    _attrs = dict(name = Attr((Variable, STR)),
                  signature = Attr(List(Variable)),
                  body = Attr((List(SyntagmathonNode), tuple)),
                  placeholder = Attr(bool, False))
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
        env[self.get_name()] = self
        return self

    def get_name(self):
        return self.name if isinstance(self.name, STR) else self.name.name

    def to_python(self, **kwargs):
        from syn.python.b import Arguments, FunctionDef, Pass

        if VER < '3':
            args = Arguments([to_python(arg, **kwargs) 
                              for arg in self.signature])
        else:
            from syn.python.b import Arg
            args = Arguments([Arg(arg.name)
                              for arg in self.signature])

        body = to_python(self.body, **kwargs)
        if not body:
            body = [Pass()]
        body[-1] = body[-1].add_return()
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
        func = self.func
        args = {name: eval(value, env, **kwargs) 
                for name, value in self.args.items()}
        if func.placeholder:
            func = env[self.func.get_name()]
            names = [name.name for name in self.func.signature]
            args = {func.signature[names.index(name)].name: value 
                    for name, value in args.items()}
        env.push(args)
        if kwargs.get('trace', False):
            depth = kwargs.get('depth', 0)
            pre = kwargs.get('tab', '  ') * depth
            argstr = ', '.join('{}={}'.format(name, value) 
                               for name, value in args.items())
            print(pre + '{}({})'.format(func.get_name(), argstr))
            kwargs['depth'] = depth + 1
        ret = func.call(env, **kwargs)
        env.pop()
        return ret

    def to_python(self, **kwargs):
        from syn.python.b import Call, Name
        args = [to_python(self.args[arg.name], **kwargs)
                for arg in self.func.signature]
        if hasattr(self.func, 'python'):
            return self.func.python(*args, **kwargs)
        func = Name(self.func.name)
        return Call(func, args)


#-------------------------------------------------------------------------------
# SpecialCall


class SpecialCall(Call):
    def eval(self, env, **kwargs):
        ret = self.func.call(env, self.args, **kwargs)
        return ret

    def to_python(self, **kwargs):
        args = [to_python(self.args[arg.name], **kwargs)
                for arg in self.func.signature]
        return self.func.python(*args, **kwargs)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Function', 'Call', 'Special', 'SpecialCall')

#-------------------------------------------------------------------------------
