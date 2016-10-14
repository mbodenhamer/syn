from syn.base_utils import get_fullname, rand_set, rand_frozenset
from .base import Type, hashable, serialize, SER_KEYS

#-------------------------------------------------------------------------------
# Set


class Set(Type):
    type = set

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
