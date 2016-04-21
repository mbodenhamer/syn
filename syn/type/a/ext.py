from functools import partial
from collections import Sequence, Mapping
from .type import TypeExtension, Type

#-------------------------------------------------------------------------------
# Callable


class Callable(TypeExtension):
    '''The value must be callable.
    '''

    def check(self, value):
        if not callable(value):
            raise TypeError('Value is not callable: {}'.format(value))


#-------------------------------------------------------------------------------
# Sequence


class Sequence(TypeExtension):
    '''The value must be a sequence whose values are the provided type.
    '''
    __slots__ = ('item_type', 'seq_type')

    def __init__(self, item_type, seq_type=Sequence):
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
# Sequence types

List = partial(Sequence, seq_type=list)
Tuple = partial(Sequence, seq_type=tuple)
Set = partial(Sequence, seq_type=set)
FrozenSet = partial(Sequence, seq_type=frozenset)

#-------------------------------------------------------------------------------
# Maping


class Mapping(TypeExtension):
    '''The value must be a mapping whose values are the provided type.
    '''
    __slots__ = ('value_type', 'map_type')

    def __init__(self, value_type, map_type=Mapping):
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
           'Mapping', 'Dict')

#-------------------------------------------------------------------------------
