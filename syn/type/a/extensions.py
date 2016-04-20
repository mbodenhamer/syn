import types
from .type import TypeExtension
from syn.base_utils import hasmethod

#-------------------------------------------------------------------------------
# Callable


class Callable(TypeExtension):
    def check(self, value):
        if (not hasmethod(value, '__call__') and 
            not isinstance(value, (types.FunctionType, 
                                   types.BuiltinFunctionType))):
            raise TypeError('Value is not callable: {}'.format(value))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Callable',)

#-------------------------------------------------------------------------------
