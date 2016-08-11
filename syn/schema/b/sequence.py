from syn.five import xrange, SET
from syn.base import Attr, init_hook
from syn.tree import Node
from syn.sets import SetNode, Union, Product, SetWrapper, TypeWrapper
from syn.base_utils import flattened, is_proper_sequence
from operator import itemgetter
from functools import partial
import collections

#-------------------------------------------------------------------------------
# SchemaNode


class SchemaNode(Node):
    _aliases = dict(_list = 'elems')
    _attrs = dict(strict = Attr(bool, False, ''),
                  set = Attr(SetNode, optional=True, internal=True,
                             doc='Internal set representation'),
                  coerce_types = Attr(bool, True, ''))
    _opts = dict(coerce_args = True)

    def __init__(self, *args, **kwargs):
        lst = []
        for arg in args:
            if isinstance(arg, SchemaNode):
                lst.append(arg)
            elif isinstance(arg, type):
                lst.append(Set(TypeWrapper(arg)))
            elif isinstance(arg, SetNode):
                lst.append(Set(arg))
            elif isinstance(arg, SET) or is_proper_sequence(arg):
                lst.append(Set(SetWrapper(arg)))
            else:
                lst.append(Set(SetWrapper([arg]))) # Create a singleton
        super(SchemaNode, self).__init__(*lst, **kwargs)


#-------------------------------------------------------------------------------
# Set


class Set(SchemaNode):
    _opts = dict(max_len = 0,
                 args = ('set',))

    def __init__(self, *args, **kwargs):
        super(SchemaNode, self).__init__(*args, **kwargs)


#-------------------------------------------------------------------------------
# Or


class Or(SchemaNode):
    _opts = dict(min_len = 2)

    def __init__(self, *args, **kwargs):
        lst = []
        for arg in args:
            if is_proper_sequence(arg):
                lst.append(Sequence(*arg))
            else:
                lst.append(arg)
        super(Or, self).__init__(*lst, **kwargs)

    @init_hook
    def generate_set(self, **kwargs):
        sets = [c.set for c in self]
        self.set = Union(*sets)


#-------------------------------------------------------------------------------
# Repeat


class Repeat(SchemaNode):
    _attrs = dict(lb = Attr(int, 0, 'Minimum number of times to repeat'),
                  ub = Attr(int, init=lambda self: self.lb + 5,
                            doc='Maximum number of times to repeat'),
                  greedy = Attr(bool, True, 'Match as much as we can'))
    _opts = dict(min_len = 1,
                 max_len = 1)

    A = property(itemgetter(0))

    @init_hook
    def generate_set(self, **kwargs):
        sets = []
        for k in xrange(self.lb, self.ub + 1):
            if k == 0:
               sets.append(SetWrapper([()]))
            elif k == 1:
                sets.append(self.A.set)
            else:
                tmp = [self.A.set] * k
                sets.append(Product(*tmp))
                
        self.set = Union(*sets)


#-------------------------------------------------------------------------------
# Sequence


class Sequence(SchemaNode):
    '''Denotes a sequence.  The only SchemaNode that can denote a sequence.'''
    _opts = dict(init_validate = True)

    @init_hook
    def generate_set(self, **kwargs):
        sets = [c.set for c in self]
        self.set = Product(*sets)

    def enumerate(self, **kwargs):
        for item in self.set.enumerate(**kwargs):
            yield flattened(item)

    def get_one(self, **kwargs):
        return flattened(self.set.get_one(**kwargs))


#-------------------------------------------------------------------------------
# Combinations

Optional = partial(Repeat, lb=0, ub=1, greedy=True)
OneOrMore = partial(Repeat, lb=1, ub=None, greedy=True)
ZeroOrMore = partial(Repeat, lb=0, ub=None, greedy=True)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('SchemaNode', 'Set', 'Or', 'Repeat', 'Sequence',
           'Optional', 'OneOrMore', 'ZeroOrMore')

#-------------------------------------------------------------------------------
