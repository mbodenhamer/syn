from random import choice
from operator import itemgetter
from syn.base_utils import type_partition, getitem

from .range import Range
from .leaf import SetWrapper, Empty
from .base import SetNode, Args

#-------------------------------------------------------------------------------
# Set Operator


class SetOperator(SetNode):
    _opts = dict(min_len = 1)

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
# Union


class Union(SetOperator):
    _opts = dict(min_len = 2)

    def hasmember(self, other):
        for c in self:
            if c.hasmember(other):
                return True
        return False

    def sample(self, **kwargs):
        c = choice([item for item in self if not isinstance(item, Empty)])
        ret = c.sample(**kwargs)
        return ret

    def enumerate(self, **kwargs):
        args = Args(**kwargs)
        maxenum = args.max_enumerate

        buf = set()
        for c in self:
            for item in c.enumerate(**kwargs):
                if len(buf) >= maxenum:
                    break
                if item not in buf:
                    buf.add(item)
                    yield item

    def to_set(self, **kwargs):
        ret = set()

        part = type_partition(self, Range, SetWrapper)
        sets = part[SetWrapper]
        ranges = part[Range]

        if sets:
            usets = sets[0].union(*sets[1:])
            ret = ret.union(usets.to_set(**kwargs))
        
        if ranges:
            uranges, remainder = ranges[0].union(*ranges[1:])
            ret = ret.union(uranges.to_set(**kwargs))
            for r in remainder:
                ret = ret.union(r.to_set(**kwargs))

        for c in part[None]:
            ret = ret.union(c.to_set(**kwargs))
        return ret


#-------------------------------------------------------------------------------
# Intersection


class Intersection(SetOperator):
    _opts = dict(min_len = 2)

    def hasmember(self, other):
        for c in self:
            if not c.hasmember(other):
                return False
        return True

    def to_set(self, **kwargs):
        ret = set()
        part = type_partition(self, Range, SetWrapper)
        sets = part[SetWrapper]
        ranges = part[Range]
        rest = part[None]
        
        if sets:
            ret = sets[0].intersection(*sets[1:]).to_set()

        if ranges:
            iranges = ranges[0].intersection(*ranges[1:])
            if ret:
                ret = ret.intersection(iranges.to_set(**kwargs))
            else:
                ret = iranges.to_set(**kwargs)

        if rest:
            if not ret:
                ret = rest[0].to_set(**kwargs)
                rest = rest[1:]
            for c in rest:
                ret = ret.intersection(c.to_set(**kwargs))

        return ret


#-------------------------------------------------------------------------------
# Difference


class Difference(SetOperator):
    _opts = dict(min_len = 2,
                 max_len = 2)

    A = property(itemgetter(0))
    B = property(itemgetter(1))

    def hasmember(self, other):
        return self.A.hasmember(other) and not self.B.hasmember(other)

    def to_set(self, **kwargs):
        if isinstance(self.A, Range) and isinstance(self.B, Range):
            A, B = self.A.difference(self.B)
            if B is None:
                return A.to_set(**kwargs)
            ret = A.to_set(**kwargs).union(B.to_set(**kwargs))
        else:
            A = self.A.to_set(**kwargs)
            B = self.B.to_set(**kwargs)
            ret = A.difference(B)

        return ret
    

#-------------------------------------------------------------------------------
# Complement


class Complement(SetOperator):
    _opts = dict(min_len = 1,
                 max_len = 1)

    A = property(itemgetter(0))

    def hasmember(self, item):
        return not self.A.hasmember(item)

    def to_set(self, **kwargs):
        universe = getitem(kwargs, 'universe', self.A.default_universe())
        
        if isinstance(self.A, Range):
            A, B = self.A.complement(universe)
            ret = A.to_set(**kwargs)
            if B:
                ret = ret.union(B.to_set(**kwargs))
        else:
            A = self.A.to_set(**kwargs)
            if not isinstance(universe, set):
                universe = universe.to_set(**kwargs)
            ret = universe.difference(A)

        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SetOperator', 'Union', 'Intersection', 'Difference', 'Complement')

#-------------------------------------------------------------------------------
