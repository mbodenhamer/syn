from random import choice
from itertools import product
from operator import itemgetter
from syn.base_utils import type_partition, prod, unzip

from .range import Range
from .leaf import SetWrapper, Empty
from .base import SetNode, Args

#-------------------------------------------------------------------------------
# Set Operator


class SetOperator(SetNode):
    def size(self):
        return len(self.to_set())

    def sample(self, **kwargs):
        buf = list(self.to_set(**kwargs))
        ret = choice(buf)
        return ret

    def get_one(self, **kwargs):
        kwargs['lazy'] = True
        return next(self.enumerate(**kwargs))

    def enumerate(self, **kwargs):
        args = Args(**kwargs)
        maxenum = args.max_enumerate

        buf = self.to_set(**kwargs)
        for k,item in enumerate(buf):
            if k >= maxenum:
                break
            yield item


#-------------------------------------------------------------------------------
# Union


class Union(SetOperator):
    def size_limits(self):
        lbs, ubs = unzip(c.size_limits() for c in self)
        # Union can't be any smaller than the biggest set (at its smallest)
        lb = max(lbs)
        # Union can't be bigger than the sum of all the sets (at their biggest)
        ub = sum(ubs)
        return (lb, ub)

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
    def size_limits(self):
        lbs, ubs = unzip(c.size_limits() for c in self)
        lb = 0
        ub = min(ubs) # Intersection can't be any bigger than its smallest set
        return (lb, ub)

    def hasmember(self, other):
        for c in self:
            if not c.hasmember(other):
                return False
        return True

    def sample(self, **kwargs):
        if not kwargs.get('lazy', False):
            return super(Intersection, self).sample(**kwargs)

        iters = 0
        args = Args(**kwargs)
        while iters < args.max_attempts:
            item = choice(self).sample(**kwargs)
            if self.hasmember(item):
                return item
            iters += 1

        raise ValueError("Unable to lazy-sample value")

    def enumerate(self, **kwargs):
        if not kwargs.get('lazy', False):
            for item in super(Intersection, self).enumerate(**kwargs):
                yield item
            
        else:
            sets = list(self)
            sets.sort(key=lambda s: s.expected_size())

            # Enumerate over the smallest set
            if sets:
                for item in sets[0].enumerate(**kwargs):
                    if self.hasmember(item):
                        yield item
                        
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

    def size_limits(self):
        lb_a, ub_a = self.A.size_limits()
        lb_b, ub_b = self.B.size_limits()

        # A at its smallest contains everything in B at its largest
        lb = lb_a - ub_b
        if lb < 0:
            lb = 0
        ub = ub_a # At at its largest contains nothing from B

        return (lb, ub)

    def hasmember(self, other):
        return self.A.hasmember(other) and not self.B.hasmember(other)

    def sample(self, **kwargs):
        if not kwargs.get('lazy', False):
            return super(Difference, self).sample(**kwargs)

        iters = 0
        args = Args(**kwargs)
        while iters < args.max_attempts:
            item = self.A.sample(**kwargs)
            if self.hasmember(item):
                return item
            iters += 1

        raise ValueError("Unable to lazy-sample value")

    def enumerate(self, **kwargs):
        if not kwargs.get('lazy', False):
            for item in super(Difference, self).enumerate(**kwargs):
                yield item
            
        else:
            for item in self.A.enumerate(**kwargs):
                if self.hasmember(item):
                    yield item

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
# Product


class Product(SetOperator):
    '''Cartesian Product'''

    def size_limits(self):
        lbs, ubs = unzip(c.size_limits() for c in self)
        lb = prod(lbs)
        ub = prod(ubs)
        return (lb, ub)

    def hasmember(self, other):
        for k, c in enumerate(self):
            if not c.hasmember(other[k]):
                return False
        return True

    def sample(self, **kwargs):
        return tuple([c.sample(**kwargs) for c in self])
    
    def enumerate(self, **kwargs):
        for item in product(*[c.enumerate(**kwargs) for c in self]):
            yield item

    def to_set(self, **kwargs):
        return set(self.enumerate(**kwargs))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SetOperator', 'Union', 'Intersection', 'Difference', 'Product')

#-------------------------------------------------------------------------------
