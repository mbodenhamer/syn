from syn.base_utils import get_fullname, rand_set, rand_frozenset
from .base import Type, hashable, serialize, SER_KEYS
from syn.base_utils.rand import HASHABLE_TYPES
from .sequence import list_enumval

#-------------------------------------------------------------------------------
# Utilities

def set_enumval(x, **kwargs):
    kwargs['types'] = kwargs.get('types', HASHBLE_TYPES)
    return list_enumval(x, **kwargs)

#-------------------------------------------------------------------------------
# Set


class Set(Type):
    type = set

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        pass

    @classmethod
    def _generate(cls, **kwargs):
        return rand_set(**kwargs)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [[serialize(item, **kwargs) for item in self.obj]]


#-------------------------------------------------------------------------------
# FrozenSet


class FrozenSet(Set):
    type = frozenset

    @classmethod
    def _generate(cls, **kwargs):
        return rand_frozenset(**kwargs)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Set', 'FrozenSet')

#-------------------------------------------------------------------------------
