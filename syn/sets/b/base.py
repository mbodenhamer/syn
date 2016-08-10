from syn.tree import Node
from syn.base import Base, Attr

#-------------------------------------------------------------------------------
# Kwargs


class Args(Base):
    _attrs = dict(max_enumerate = Attr(int, 1000, ''),
                  type_enumerate = Attr(int, 50, ''),
                  enumerated = Attr(int, 0, ''),
                  lazy = Attr(bool, False, ''),
                  max_attempts = Attr(int, 500, ''))


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

    def size(self):
        '''Returns the cardinality of the set.
        '''
        raise NotImplementedError()

    def size_limits(self):
        '''Returns the lower and upper bounds of set size.
        '''
        return (self.size(), self.size())

    def expected_size(self):
        lb, ub = self.size_limits()
        return (ub + lb) / 2.0

    def union(self, *args):
        raise NotImplementedError()

    def intersection(self, *args):
        raise NotImplementedError()

    def difference(self, other):
        raise NotImplementedError()

    def complement(self, universe):
        raise NotImplementedError()

    def issubset(self, other):
        raise NotImplementedError()

    def issuperset(self, other):
        raise NotImplementedError()

    def hasmember(self, item):
        raise NotImplementedError()

    def simplify(self):
        raise NotImplementedError()

    def sample(self, **kwargs):
        '''Return a random element from the set.  Method should try to avoid introducing a sampling bias.
        '''
        raise NotImplementedError()

    def get_one(self, **kwargs):
        '''Return one element from the set, regardless of sampling bias, without evaluating any sets.
        '''
        kwargs['lazy'] = True
        return self.sample(**kwargs)

    def lazy_sample(self, **kwargs):
        '''Sample without evaluating any sets.
        '''
        kwargs['lazy'] = True
        return self.sample(**kwargs)

    def enumerate(self, **kwargs):
        raise NotImplementedError()

    def lazy_enumerate(self, **kwargs):
        '''Enumerate without evaluating any sets.
        '''
        kwargs['lazy'] = True
        for item in self.enumerate(**kwargs):
            yield item
        
    def to_set(self, **kwargs):
        return set(self.enumerate(**kwargs))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('SetNode',)

#-------------------------------------------------------------------------------
