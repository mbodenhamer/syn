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
# Set Operator


class SetOperator(SetNode):
    _opts = dict(min_len = 1,
                 convertmap = {})

    def sample(self, **kwargs):
        buf = list(self.to_set(**kwargs))
        ret = choice(buf)
        return ret

    def enumerate(self, **kwargs):
        args = Args(kwargs)
        maxenum = args.max_enumerate

        buf = self.to_set(**kwargs)
        for k,item in enumerate(buf):
            if k >= maxenum:
                break
            yield item


#-------------------------------------------------------------------------------
# Set Leaf


class SetLeaf(SetNode):
    _opts = dict(coerce_args = True,
                 convertmap = {},
                 max_len = 0)

    def simplify(self):
        return self


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SetNode', 'SetOperator', 'SetLeaf')

#-------------------------------------------------------------------------------
