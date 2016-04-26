from functools import partial
from collections import Sequence as _Sequence
from collections import Mapping as _Mapping
from .type import TypeExtension, Type
from syn.base_utils import is_hashable

#-------------------------------------------------------------------------------
# Callable


class Callable(TypeExtension):
    '''The value must be callable.
    '''

    def check(self, value):
        if not callable(value):
            raise TypeError('Value is not callable: {}'.format(value))


#-------------------------------------------------------------------------------
# Hashable


class Hashable(TypeExtension):
    '''The value must be hashable.
    '''

    def check(self, value):
        if not is_hashable(value):
            raise TypeError('Value is not hashable: {}'.format(value))


#-------------------------------------------------------------------------------
# Sequence


class Sequence(TypeExtension):
    '''The value must be a sequence whose values are the provided type.
    '''
    __slots__ = ('item_type', 'seq_type')

    def __init__(self, item_type, seq_type=_Sequence):
        self.item_type = Type.dispatch(item_type)
        self.seq_type = Type.dispatch(seq_type)

    def check(self, values):
        self.seq_type.check(values)

        for value in values:
            self.item_type.check(value)

    def coerce(self, values):
        if not self.query(values):
            newvals = [self.item_type.coerce(value) for value in values]
            return self.seq_type.coerce(newvals)
        return values


#-------------------------------------------------------------------------------
# Tuple


class Tuple(TypeExtension):
    '''For defining tuple types.
    '''
    __slots__ = ('types', 'length', 'uniform')

    def __init__(self, types, length=None, uniform=False):
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


#-------------------------------------------------------------------------------
# Sequence types

List = partial(Sequence, seq_type=list)
Set = partial(Sequence, seq_type=set)
FrozenSet = partial(Sequence, seq_type=frozenset)
AssocList = List(Tuple((None, None)))

#-------------------------------------------------------------------------------
# Maping


class Mapping(TypeExtension):
    '''The value must be a mapping whose values are the provided type.
    '''
    __slots__ = ('value_type', 'map_type')

    def __init__(self, value_type, map_type=_Mapping):
        self.value_type = Type.dispatch(value_type)
        self.map_type = Type.dispatch(map_type)

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


#-------------------------------------------------------------------------------
# Mapping types

Dict = partial(Mapping, map_type=dict)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Callable', 'Sequence', 'List', 'Tuple', 'Set', 'FrozenSet',
           'Mapping', 'Dict', 'Hashable', 'AssocList')

#-------------------------------------------------------------------------------
