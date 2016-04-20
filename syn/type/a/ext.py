import types
from functools import partial
from collections import Sequence
from .type import TypeExtension, Type
from syn.base_utils import hasmethod

#-------------------------------------------------------------------------------
# Callable


class Callable(TypeExtension):
    '''The value must be callable.
    '''

    def check(self, value):
        if (not hasmethod(value, '__call__') and 
            not isinstance(value, (types.FunctionType, 
                                   types.BuiltinFunctionType))):
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
# __all__

__all__ = ('Callable', 'Sequence', 'List', 'Tuple', 'Set', 'FrozenSet')

#-------------------------------------------------------------------------------
