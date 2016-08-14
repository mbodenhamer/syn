from random import choice
from functools import reduce
from syn.base import Attr, init_hook
from syn.type import List, Type
from syn.base_utils import subclasses, rand_dispatch
from .base import SetNode, Args

#-------------------------------------------------------------------------------
# Decorators

def _set_wrapper(f):
    def func(self, *args, **kwargs):
        lst = []
        for arg in args:
            if not isinstance(arg, (set, SetWrapper, Empty)):
                raise TypeError("Invalid argument type: '%s'" % type(arg))

            if isinstance(arg, Empty):
                arg = set()

            if isinstance(arg, set):
                lst.append(arg)
            else:
                lst.append(arg.set)

        ret = f(self, *lst, **kwargs)
        return ret
    return func

#-------------------------------------------------------------------------------
# Set Leaf


class SetLeaf(SetNode):
    _opts = dict(coerce_args = True,
                 max_len = 0)

    def __init__(self, *args, **kwargs):
        super(SetNode, self).__init__(*args, **kwargs)


#-------------------------------------------------------------------------------
# Set Wrapper


class SetWrapper(SetLeaf):
    _attrs = dict(set = Attr(set, doc=''))
    _opts = dict(args = ('set',))

    def size(self):
        return len(self.set)

    @_set_wrapper
    def union(self, *args):
        ret = reduce(set.union, (self.set,) + args)
        return type(self)(ret)

    @_set_wrapper
    def intersection(self, *args):
        ret = reduce(set.intersection, (self.set,) + args)
        return type(self)(ret)

    @_set_wrapper
    def difference(self, other):
        ret = self.set.difference(other)
        return type(self)(ret)

    @_set_wrapper
    def complement(self, universe):
        ret = universe.difference(self.set)
        return type(self)(ret)

    @_set_wrapper
    def issubset(self, other):
        return self.set.issubset(other)

    @_set_wrapper
    def issuperset(self, other):
        return self.set.issuperset(other)

    def hasmember(self, item):
        return item in self.set

    def sample(self, **kwargs):
        ret = choice(list(self.set))
        return ret

    def enumerate(self, **kwargs):
        args = Args(**kwargs)
        maxenum = args.max_enumerate

        for k,item in enumerate(self.set):
            if k >= maxenum:
                break
            yield item

    def to_set(self, **kwargs):
        return set(self.set)


#-------------------------------------------------------------------------------
# TypeWrapper


class TypeWrapper(SetLeaf):
    '''The idea is that a type implicitly represents the set of all of its
    valid instances.
    '''
    _attrs = dict(type = Attr(Type, doc=''))
    _opts = dict(args = ('type',),
                 coerce_args = False)

    @init_hook
    def _convert_type(self):
        if not isinstance(self.type, Type):
            self.type = Type.dispatch(self.type)

    def size(self):
        return float('inf')

    def hasmember(self, item):
        return self.type.query(item)

    def sample(self, **kwargs):
        return self.type.generate(**kwargs)

    def enumerate(self, **kwargs):
        args = Args(**kwargs)
        maxenum = min(args.max_enumerate, args.type_enumerate)

        for k in range(maxenum):
            item = self.sample(**kwargs)
            yield item

    def to_set(self, **kwargs):
        return super(SetLeaf, self).to_set(**kwargs)


#-------------------------------------------------------------------------------
# ClassWrapper


class ClassWrapper(SetLeaf):
    '''The idea is that a type implicitly represents the set of all of its
    subclasses, including itself.
    '''
    _attrs = dict(type = Attr(type, doc=''),
                  subclasses = Attr(List(type), doc='',
                                    init=lambda self: ([self.type] + 
                                                       subclasses(self.type))))
    _opts = dict(args = ('type',))


    def __init__(self, *args, **kwargs):
        super(ClassWrapper, self).__init__(*args, **kwargs)
        self.subclasses = [self.type] + subclasses(self.type)

    def size(self):
        return len(self.subclasses)

    def hasmember(self, item):
        return item in self.subclasses

    def sample(self, **kwargs):
        ret = choice(self.subclasses)
        return ret

    def enumerate(self, **kwargs):
        args = Args(**kwargs)
        maxenum = min(args.max_enumerate, len(self.subclasses))

        for k, item in enumerate(self.subclasses):
            if k >= maxenum:
                break
            yield item

    def to_set(self, **kwargs):
        return super(SetLeaf, self).to_set(**kwargs)


#-------------------------------------------------------------------------------
# Special


class Special(SetLeaf):
    pass


#-----------------------------------------------------------
# Empty


class Empty(Special):
    def size(self):
        return 0
    
    def issubset(self, other):
        return True

    def issuperset(self, other):
        if isinstance(other, Empty) or other.size() == 0:
            return True
        return False

    def hasmember(self, other):
        return False

    def overlaps(self, other):
        return False

    def enumerate(self, **kwargs):
        # A generator that never emits anything
        if False:
            yield None # pragma: no cover

    def to_set(self, **kwargs):
        return set()


NULL = Empty()

#-------------------------------------------------------------------------------
# __all__

__all__ = ('SetLeaf', 'SetWrapper', 'TypeWrapper', 'ClassWrapper',
           'Special', 'Empty', 'NULL')

#-------------------------------------------------------------------------------
