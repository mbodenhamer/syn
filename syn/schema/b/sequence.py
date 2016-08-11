from syn.base import Attr
from syn.tree import Node

#-------------------------------------------------------------------------------
# SchemaNode


class SchemaNode(Node):
    _aliases = dict(_list = 'elems')
    _attrs = dict(strict = Attr(bool, False, ''),
                  coerce_types = Attr(bool, True, ''))
    _opts = dict(coerce_args = True)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SchemaNode',)

#-------------------------------------------------------------------------------
