from syn.types.a import enumerate as enum
from syn.base.b import Attr
from syn.tree.b import Node
from syn.five import STR

#-------------------------------------------------------------------------------
# Base Class


class SyntagmathonNode(Node):
    _opts = dict(max_len = 0)

    def eval(self, env, **kwargs):
        raise NotImplementedError

    def to_python(self, **kwargs):
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Variable


class Variable(SyntagmathonNode):
    _attrs = dict(name = Attr(STR))
    _opts = dict(args = ('name',))

    def __call__(self, *args):
        from .function import Function
        names = enum(str, max_enum=len(args))
        func = Function(self.name, 
                        [Variable(name) for name in names],
                        [],
                        placeholder=True)
        return func(*args)

    def eval(self, env, **kwargs):
        return env[self.name]

    def to_python(self, **kwargs):
        from syn.python.b import Name
        return Name(self.name)


#-------------------------------------------------------------------------------
# Utilities

def vars(*args):
    if len(args) == 1:
        args = args[0].split()
    if len(args) == 1:
        return Variable(args[0])
    return tuple([Variable(arg) for arg in args])

#-------------------------------------------------------------------------------
# __all__

__all__ = ('SyntagmathonNode',
           'Variable', 'vars')

#-------------------------------------------------------------------------------
