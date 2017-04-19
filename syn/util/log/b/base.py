from syn.tree.b import Node, Tree
from syn.base.b import Attr

#-------------------------------------------------------------------------------
# Event


class Event(Node):
    pass


#-------------------------------------------------------------------------------
# Logger


class Logger(Tree):
    _opts = dict(init_validate = True)
    _attrs = dict(root = Attr(Event))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Event', 'Logger')

#-------------------------------------------------------------------------------
