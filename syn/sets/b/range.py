from random import randint
from functools import reduce
from syn.base import Attr, init_hook
from syn.five import xrange, unichr, STR
from syn.base_utils import defer_reduce
from syn.base_utils.rand import MIN_INT, MAX_INT

from .base import Args
from .leaf import SetLeaf, NULL

#-------------------------------------------------------------------------------
# Range


class Range(SetLeaf):
    _attrs = dict(lb = Attr(int, doc='The lower bound'),
                  ub = Attr(int, doc='The upper bound'))
    _opts = dict(args = ('lb', 'ub'))

    def size(self):
        return self.ub - self.lb + 1

    def validate(self):
        super(Range, self).validate()

        if self.lb > self.ub:
            raise ValueError("Invalid interval bounds")

    def overlaps(self, other):
        if isinstance(other, type(self)):
            if self.lb <= other.lb <= self.ub:
                return True

            if other.lb <= self.lb <= other.ub:
                return True

        return False

    @classmethod
    def _union(cls, a, b):
        if a is NULL and b is NULL:
            return NULL
        if a is NULL:
            return b
        if b is NULL:
            return a

        if a.lb <= b.lb and b.ub >= a.ub:
            return cls(a.lb, b.ub)
        elif a.lb <= b.lb:
            return a
        elif b.lb <= a.lb and a.ub <= b.ub:
            return b
        else:
            return cls(b.lb, a.ub)

    def union(self, *args):
        if not args:
            return self, []

        test = lambda item, accum: item.overlaps(accum) or accum is NULL
        return defer_reduce(type(self)._union, (self,) + args, test, NULL)

    @classmethod
    def _intersection(cls, a, b):
        if a is NULL or b is NULL:
            return NULL

        if not a.overlaps(b):
            return NULL

        if a.lb <= b.lb and b.ub >= a.ub:
            return cls(b.lb, a.ub)
        elif a.lb <= b.lb:
            return b
        elif b.lb <= a.lb and a.ub <= b.ub:
            return a
        else:
            return cls(a.lb, b.ub)

    def intersection(self, *args):
        if not args:
            return self

        ret = reduce(type(self)._intersection, (self,) + args)
        return ret

    def difference(self, other):
        if other is NULL:
            return self, None
            
        if not self.overlaps(other):
            return self, None

        a = self
        b = other
        cls = type(self)

        if a.lb < b.lb and b.ub >= a.ub:
            return cls(a.lb, b.lb - 1), None
        elif a.lb < b.lb:
            return cls(a.lb, b.lb - 1), cls(b.ub + 1, a.ub)
        elif b.lb < a.lb and a.ub < b.ub:
            return NULL, None
        else:
            return cls(b.ub + 1, a.ub), None

    def complement(self, universe):
        ret = universe.difference(self)
        return ret

    def issubset(self, other):
        return self.lb >= other.lb and self.ub <= other.ub

    def issuperset(self, other):
        return self.lb <= other.lb and self.ub >= other.ub

    def hasmember(self, other):
        return self.lb <= other <= self.ub

    def sample(self, **kwargs):
        ret = randint(self.lb, self.ub)
        return ret

    def enumerate(self, **kwargs):
        args = Args(**kwargs)
        maxenum = args.max_enumerate

        for k,item in enumerate(xrange(self.lb, self.ub + 1)):
            if k >= maxenum:
                break
            yield item

    def to_set(self, **kwargs):
        args = Args(**kwargs)
        N = self.ub - self.lb
        ub = self.lb + min(N, args.max_enumerate - 1)

        ret = set(range(self.lb, ub + 1))
        return ret


#-------------------------------------------------------------------------------
# IntRange


class IntRange(Range):
    def hasmember(self, other):
        if isinstance(other, int):
            return super(IntRange, self).hasmember(other)
        return False


Integers = IntRange(MIN_INT, MAX_INT)
Naturals = IntRange(0, MAX_INT)

#-------------------------------------------------------------------------------
# StrRange


class StrRange(Range):
    _attrs = dict(lb = Attr(int, 0x20, doc='The lower bound'),
                  ub = Attr(int, 0x7e, doc='The upper bound'))
    _opts = dict(coerce_args = False)

    @init_hook
    def _ensure_ints(self):
        if isinstance(self.lb, STR):
            self.lb = ord(self.lb)
        
        if isinstance(self.ub, STR):
            self.ub = ord(self.ub)
    
    def hasmember(self, other):
        return super(StrRange, self).hasmember(ord(other))

    def sample(self, **kwargs):
        ret = super(StrRange, self).sample()
        return unichr(ret)

    def enumerate(self, **kwargs):
        for item in super(StrRange, self).enumerate(**kwargs):
            yield unichr(item)

    def to_set(self, **kwargs):
        return super(Range, self).to_set(**kwargs)


ASCII = StrRange(0x20, 0x7e)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Range', 'IntRange', 'StrRange')

#-------------------------------------------------------------------------------
