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

    def eval(self, env, **kwargs):
        return env[self.name]


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SyntagmathonNode',
           'Variable')

#-------------------------------------------------------------------------------
