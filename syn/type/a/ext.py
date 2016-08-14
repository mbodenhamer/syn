from random import randint
from functools import partial
from syn.five import xrange
from collections import Sequence as _Sequence
from collections import Mapping as _Mapping
from .type import TypeExtension, Type, AnyType
from syn.base_utils import is_hashable, rand_hashable
from syn.base_utils.rand import MIN_SEQLEN, MAX_SEQLEN, rand_str

#-------------------------------------------------------------------------------
# Callable


class Callable(TypeExtension):
    '''The value must be callable.
    '''

    def check(self, value):
        if not callable(value):
            raise TypeError('Value is not callable: {}'.format(value))

    def display(self):
        return '<callable>'

    def generate(self, **kwargs):
        def func(*args, **_kwargs):
            return args, _kwargs
        return func


#-------------------------------------------------------------------------------
# Hashable


class Hashable(TypeExtension):
    '''The value must be hashable.
    '''

    def check(self, value):
        if not is_hashable(value):
            raise TypeError('Value is not hashable: {}'.format(value))

    def display(self):
        return '<hashable>'

    def generate(self, **kwargs):
        return rand_hashable(**kwargs)


#-------------------------------------------------------------------------------
# Sequence


class Sequence(TypeExtension):
    '''The value must be a sequence whose values are the provided type.
    '''
    __slots__ = ('item_type', 'seq_type')
    register_generable = True

    def __init__(self, item_type, seq_type=_Sequence):
        super(Sequence, self).__init__()
        self.item_type = Type.dispatch(item_type)
        self.seq_type = Type.dispatch(seq_type)

    def __eq__(self, other):
        if super(Sequence, self).__eq__(other):
            if self.seq_type == other.seq_type:
                if self.item_type == other.item_type:
                    return True
        return False

    def __hash__(self):
        return hash(id(self))

    def check(self, values):
        self.seq_type.check(values)

        for value in values:
            self.item_type.check(value)

    def coerce(self, values):
        if not self.query(values):
            newvals = [self.item_type.coerce(value) for value in values]
            return self.seq_type.coerce(newvals)
        return values
        
    def display(self):
        seq = self.seq_type.display()
        item = self.item_type.display()
        return '{}({})'.format(seq, item)

    def generate(self, **kwargs):
        min_len = kwargs.get('min_len', MIN_SEQLEN)
        max_len = kwargs.get('max_len', MAX_SEQLEN)
        N = randint(min_len, max_len)
        ret = [self.item_type.generate(**kwargs) for k in xrange(N)]
        return self.seq_type.coerce(ret)

    def rst(self):
        seq = self.seq_type.rst()
        item = self.item_type.rst()
        return '{} ({})'.format(seq, item)


#-------------------------------------------------------------------------------
# Tuple


class Tuple(TypeExtension):
    '''For defining tuple types.
    '''
    __slots__ = ('types', 'length', 'uniform')
    register_generable = True

    def __init__(self, types, length=None, uniform=False):
        super(Tuple, self).__init__()
        self.uniform = True
        if isinstance(types, _Sequence) and not uniform:
            length = len(types)
            self.uniform = False

        if self.uniform:
            types = Type.dispatch(types)
        else:
            types = [Type.dispatch(typ) for typ in types]

        self.types = types
        self.length = length

    def __eq__(self, other):
        if super(Tuple, self).__eq__(other):
            if self.types == other.types:
                if self.uniform == other.uniform:
                    if self.length == other.length:
                        return True
        return False

    def __hash__(self):
        return hash(id(self))

    def check(self, values):
        if not isinstance(values, tuple):
            raise TypeError('Value must be type tuple')

        if self.length is not None:
            if len(values) != self.length:
                raise TypeError('Tuple must be length {}'.format(self.length))

        if self.uniform:
            for value in values:
                self.types.check(value)
        else:
            for k, typ in enumerate(self.types):
                typ.check(values[k])

    def coerce(self, values):
        if self.query(values):
            return values

        if self.length is not None:
            if len(values) != self.length:
                raise TypeError('Tuple must be length {}'.format(self.length))

        if self.uniform:
            values = [self.types.coerce(value) for value in values]
        else:
            values = [typ.coerce(values[k]) for k, typ in enumerate(self.types)]
        return tuple(values)

    def display(self):
        types = self.types
        if self.uniform and self.length:
            types = [types] * self.length

        if not self.length:
            ret = '{}, ...'.format(self.types.display())
        else:
            ret = ', '.join(t.display() for t in types)
        return '(' + ret + ')'

    def generate(self, **kwargs):
        types = self.types
        if self.uniform and self.length:
            types = [types] * self.length

        if not self.length:
            min_len = kwargs.get('min_len', MIN_SEQLEN)
            max_len = kwargs.get('max_len', MAX_SEQLEN)
            N = randint(min_len, max_len)
            ret = [self.types.generate(**kwargs) for k in xrange(N)]
        else:
            ret = [t.generate(**kwargs) for t in types]
        return tuple(ret)

    def rst(self):
        types = self.types
        if self.uniform and self.length:
            types = [types] * self.length

        if not self.length:
            ret = '{}, ...'.format(self.types.rst())
        else:
            ret = ', '.join(t.rst() for t in types)
        return '(' + ret + ')'


#-------------------------------------------------------------------------------
# Sequence types

List = partial(Sequence, seq_type=list)
#Set = partial(Sequence, seq_type=set)
#FrozenSet = partial(Sequence, seq_type=frozenset)
AssocList = List(Tuple((None, None)))

#-------------------------------------------------------------------------------
# Maping


class Mapping(TypeExtension):
    '''The value must be a mapping whose values are the provided type.
    '''
    __slots__ = ('value_type', 'map_type')
    register_generable = True

    def __init__(self, value_type, map_type=_Mapping):
        super(Mapping, self).__init__()
        self.value_type = Type.dispatch(value_type)
        self.map_type = Type.dispatch(map_type)

    def __eq__(self, other):
        if super(Mapping, self).__eq__(other):
            if self.map_type == other.map_type:
                if self.value_type == other.value_type:
                    return True
        return False

    def __hash__(self):
        return hash(id(self))

    def check(self, dct):
        self.map_type.check(dct)

        for value in dct.values():
            self.value_type.check(value)

    def coerce(self, dct):
        if not self.query(dct):
            newdct = {key:self.value_type.coerce(value) for key,value in
                      dct.items()}
            return self.map_type.coerce(newdct)
        return dct

    def display(self):
        map_ = self.map_type.display()
        value = self.value_type.display()
        return '{}({} => {})'.format(map_, AnyType().display(), value)

    def generate(self, **kwargs):
        min_len = kwargs.get('min_len', MIN_SEQLEN)
        max_len = kwargs.get('max_len', MAX_SEQLEN)
        N = randint(min_len, max_len)
        
        values = [self.value_type.generate(**kwargs) for k in xrange(N)]
        keys = [rand_str(min_len=5, max_len=10) for k in xrange(N)]
        ret = dict(zip(keys, values))
        return self.map_type.coerce(ret)

    def rst(self):
        map_ = self.map_type.rst()
        value = self.value_type.rst()
        return '{} ({} => {})'.format(map_, AnyType().rst(), value)


#-------------------------------------------------------------------------------
# Mapping types

Dict = partial(Mapping, map_type=dict)

#-------------------------------------------------------------------------------
# This (for recursive type definitions)


class This(TypeExtension):
    pass


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Callable', 'Sequence', 'List', 'Tuple',
           'Mapping', 'Dict', 'Hashable', 'AssocList', 'This')

#-------------------------------------------------------------------------------
