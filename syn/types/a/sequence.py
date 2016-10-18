import collections
from syn.base_utils import rand_list, rand_tuple, get_fullname, tuple_prepend
from .base import Type, hashable, deserialize, serialize, SER_KEYS

#-------------------------------------------------------------------------------
# Sequence


class Sequence(Type):
    type = collections.Sequence

    @classmethod
    def deserialize(cls, seq, **kwargs):
        if not isinstance(seq, collections.Sequence):
            return super(Sequence, cls).deserialize(seq, **kwargs)

        ret = [deserialize(item, **kwargs) for item in seq]
        return cls.type(ret)

    def _hashable(self, **kwargs):
        tup = tuple([hashable(item) for item in self.obj])
        return tuple_prepend(get_fullname(self.obj), tup)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [[serialize(item, **kwargs) for item in self.obj]]


#-------------------------------------------------------------------------------
# Sequences


class List(Sequence):
    type = list

    @classmethod
    def _generate(cls, **kwargs):
        # TODO: pull types from registry (unless they are marked as
        # excluded or included in an exclude parameter set)
        return rand_list(**kwargs)
    

class Tuple(Sequence):
    type = tuple

    @classmethod
    def _generate(cls, **kwargs):
        return rand_tuple(**kwargs)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Sequence',
           'List', 'Tuple')

#-------------------------------------------------------------------------------
