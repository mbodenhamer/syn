'''Tools for representing sets of sequences via sequence operators and
sets of sequence items.  The main idea is that a set of sequences is
the result of a (flattened) Cartesian product over a sequence of sets.
'''

from copy import copy
from syn.five import xrange, SET, STR
from syn.base import Attr, init_hook, Base, ListWrapper
from syn.tree import Node
from syn.sets import SetNode, Union, Product, SetWrapper, TypeWrapper
from syn.base_utils import flattened, is_proper_sequence, IterableList, message
from operator import itemgetter
from functools import partial

OAttr = partial(Attr, optional=True)

#-------------------------------------------------------------------------------
# Match


class Match(ListWrapper):
    # So that "if pattern.match(...):" can be used
    def __nonzero__(self):
        return True

    def __bool__(self):
        return True


#-------------------------------------------------------------------------------
# MatchFailure


class MatchFailure(Base):
    _attrs = dict(message = Attr(STR, doc='Reason for failure'),
                  seq = Attr(IterableList, 
                             doc='The sequence that failed to match'),
                  fails = OAttr(list, doc='List of sub-failures'))
    _opts = dict(init_validate = True)

    # So that "if pattern.match(...):" can be used
    def __nonzero__(self):
        return False

    def __bool__(self):
        return False


#-------------------------------------------------------------------------------
# MatchFailed


class MatchFailed(Exception):
    def __init__(self, msg, seq, fails=None):
        super(MatchFailed, self).__init__(msg)
        self.seq = seq
        self.fails = fails if fails else []
    
    def failure(self):
        return MatchFailure(message=message(self), 
                            seq=self.seq, 
                            fails=self.fails)


#-------------------------------------------------------------------------------
# SchemaNode


class SchemaNode(Node):
    _aliases = dict(_list = ['elems'])
    _attrs = dict(set = Attr(SetNode, optional=True, internal=True,
                             doc='Internal set representation'))
    _opts = dict(optional_none = True)

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

    def match(self, seq, **kwargs):
        match = kwargs['match']

        try:
            seq.mark()
            item = next(seq)
        except StopIteration:
            raise MatchFailed('Sequence is too short', seq)

        if self.set.hasmember(item):
            match.append(item)
        else:
            seq.reset() # Correct the index for error display
            raise MatchFailed('Item not in set', seq)


#-------------------------------------------------------------------------------
# Type


class Type(Set):
    def __init__(self, arg, **kwargs):
        if not isinstance(arg, TypeWrapper):
            arg = TypeWrapper(arg)
        super(Type, self).__init__(arg, **kwargs)


#-------------------------------------------------------------------------------
# Or


class Or(SchemaNode):
    _opts = dict(min_len = 2)

    @init_hook
    def generate_set(self, **kwargs):
        sets = [c.set for c in self]
        self.set = Union(*sets)

    def match(self, seq, **kwargs):
        match = kwargs['match']
        mark = seq.position

        fails = []
        passed = False
        for elem in self.elems:
            match2 = copy(match)
            seq2 = seq.copy()
            kwargs['match'] = match2
            try:
                elem.match(seq2, **kwargs)
                passed = True
                match.extend(seq.take(seq2.position - mark))
                break
            except MatchFailed as e:
                fails.append(e.failure())

        if not passed:
            raise MatchFailed('Did not meet any Or conditions', seq, fails)


#-------------------------------------------------------------------------------
# Repeat


class Repeat(SchemaNode):
    _attrs = dict(lb = Attr(int, 0, 'Minimum number of times to repeat'),
                  ub = OAttr(int, doc='Maximum number of times to repeat'),
                  greedy = Attr(bool, True, 'Match as much as we can if True'))
    _opts = dict(min_len = 1,
                 max_len = 1)

    A = property(itemgetter(0))

    @init_hook
    def generate_set(self, **kwargs):
        ub = self.ub if self.ub is not None else self.lb + 5

        sets = []
        for k in xrange(self.lb, ub + 1):
            if k == 0:
               sets.append(SetWrapper([()]))
            elif k == 1:
                sets.append(self.A.set)
            else:
                tmp = [self.A.set] * k
                sets.append(Product(*tmp))
                
        self.set = Union(*sets)

    def match(self, seq, **kwargs):
        mark = seq.position
        count = 0
        seq2 = seq.copy()
        match = kwargs['match']
        match2 = copy(match)
        kwargs['match'] = match2

        fails = []
        while True:
            try:
                self.A.match(seq2, **kwargs)
                count += 1
                match.extend(seq.take(seq2.position - mark))
                mark = seq.position
                
                if not self.greedy:
                    if count >= self.lb:
                        break

                if self.ub is not None:
                    if count >= self.ub:
                        break
            
            except MatchFailed as e:
                fails.append(e.failure())
                break
                
        if count < self.lb:
            raise MatchFailed('Did not match enough repetitions', seq, fails)

    def validate(self):
        super(Repeat, self).validate()

        if self.ub is not None:
            if self.lb > self.ub:
                raise ValueError('Lower bound greater than upper bound')
        

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
        '''Iterate through all possible sequences (lists).  By default, will
        stop after 50 items have been yielded. This value can be
        change by supplying a different value via the max_enumerate kwarg.
        '''
        for item in self.set.enumerate(**kwargs):
            yield flattened(item)

    def get_one(self, **kwargs):
        '''Returns one possible sequence (list). May return the same value on
        multiple invocations.
        '''
        return flattened(self.set.get_one(**kwargs))

    def match(self, seq, **kwargs):
        '''If the schema matches seq, returns a list of the matched objects.
        Otherwise, returns MatchFailure instance.
        '''
        strict = kwargs.get('strict', False)
        top_level = kwargs.get('top_level', True)
        match = kwargs.get('match', list())

        if top_level:
            kwargs['top_level'] = False
            kwargs['match'] = match

            try:
                seq = IterableList(seq)
                self.match(seq, **kwargs)

                if strict:
                    if not seq.empty():
                        raise MatchFailed('Sequence is too long', seq)

            except MatchFailed as e:
                return e.failure()

            return Match(*match)

        for elem in self.elems:
            elem.match(seq, **kwargs)

    def sample(self, **kwargs):
        '''Returns one possible sequence (list). The selection is randomized.
        '''
        return flattened(self.set.sample(**kwargs))

    def validate(self):
        super(Sequence, self).validate()
        self.set.validate()


#-------------------------------------------------------------------------------
# Combinations

Optional = partial(Repeat, lb=0, ub=1, greedy=True)
OneOrMore = partial(Repeat, lb=1, greedy=True)
ZeroOrMore = partial(Repeat, lb=0, greedy=True)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('SchemaNode', 'Set', 'Type', 'Or', 'Repeat', 'Sequence',
           'Match', 'MatchFailure', 'MatchFailed',
           'Optional', 'OneOrMore', 'ZeroOrMore')

#-------------------------------------------------------------------------------
