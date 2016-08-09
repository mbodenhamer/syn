from random import choice
from syn.tree import Node
from syn.base import Base, Attr

#-------------------------------------------------------------------------------
# Kwargs


class Args(Base):
    _attrs = dict(max_enumerate = Attr(int, 1000, ''),
                  type_enumerate = Attr(int, 50, ''),
                  enumerated = Attr(int, 0, ''))


#-------------------------------------------------------------------------------
# SetNode


class SetNode(Node):
    def __init__(self, *args, **kwargs):
        from .leaf import SetWrapper

        lst = []
        for arg in args:
            if isinstance(arg, SetNode):
                lst.append(arg)
            else:
                lst.append(SetWrapper(arg))
        super(SetNode, self).__init__(*lst, **kwargs)

    def union(self, *args):
        raise NotImplementedError()

    def intersection(self, *args):
        raise NotImplementedError()

    def difference(self, other):
        raise NotImplementedError()

    def complement(self, universe):
        raise NotImplementedError()

    def default_universe(self):
        return self

    def issubset(self, other):
        raise NotImplementedError()

    def issuperset(self, other):
        raise NotImplementedError()

    def hasmember(self, item):
        raise NotImplementedError()

    def simplify(self):
        raise NotImplementedError()

    def sample(self, **kwargs):
        raise NotImplementedError()

    def enumerate(self, **kwargs):
        raise NotImplementedError()

    def to_set(self, **kwargs):
        return set(self.enumerate(**kwargs))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SetNode',)

#-------------------------------------------------------------------------------
