import collections
from syn.five import xrange
from syn.base_utils import rand_list, rand_tuple, get_fullname, tuple_prepend, \
    get_typename, escape_for_eval
from .base import Type, hashable, deserialize, serialize, SER_KEYS, rstr, estr
from syn.base_utils.rand import SEQ_TYPES, MAX_DEPTH, PRIMITIVE_TYPES
from .ne import DiffersAtIndex, DifferentLength

#-------------------------------------------------------------------------------
# Utilities

def list_enumval(x, **kwargs):
    top_level = kwargs.get('top_level', True)
    if top_level:
        if x == 0:
            return []

        kwargs['top_level'] = False
        return list_enumval(x - 1, **kwargs)

    depth = kwargs.get('depth', 0)
    max_depth = kwargs.get('max_depth', MAX_DEPTH)
    types = kwargs.get('types', SEQ_TYPES)

    if depth >= max_depth:
        types = [t for t in types if t in PRIMITIVE_TYPES]

    kwargs['depth'] = depth + 1

    N = len(types)
    i = x % N
    j = x // N
    l = j + 1

    ret = []
    for k in xrange(l):
        i_k = (i + k) % N
        x_k = j + (k // N)
        item = Type.type_dispatch(types[i_k])._enumeration_value(x_k, **kwargs)
        ret.append(item)
    return ret

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

    def estr(self, **kwargs):
        parts = [estr(item, **kwargs) for item in self.obj]
        ret = '[' + ', '.join(parts) + ']'
        ret = '{}({})'.format(get_typename(self.obj), ret)
        return escape_for_eval(ret)

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return list_enumval(x, **kwargs)

    def _find_ne(self, other, func, **kwargs):
        for k, item in enumerate(self.obj):
            if k >= len(other):
                return DifferentLength(self.obj, other)
            if not func(item, other[k]):
                return DiffersAtIndex(self.obj, other, k)
        return DifferentLength(self.obj, other)

    def _hashable(self, **kwargs):
        tup = tuple([hashable(item) for item in self.obj])
        return tuple_prepend(get_fullname(self.obj), tup)

    def _rstr(self, **kwargs):
        # TODO: add pretty option
        parts = [rstr(item, **kwargs) for item in self.obj]
        ret = '[' + ', '.join(parts) + ']'
        return ret

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [[serialize(item, **kwargs) for item in self.obj]]

    def _visit(self, k, **kwargs):
        return self.obj[k]

    def _visit_len(self, **kwargs):
        return len(self.obj)


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
    def _enumeration_value(cls, x, **kwargs):
        return tuple(super(Tuple, cls)._enumeration_value(x, **kwargs))

    @classmethod
    def _generate(cls, **kwargs):
        return rand_tuple(**kwargs)

    def _rstr(self, **kwargs):
        ret = super(Tuple, self)._rstr(**kwargs)[1:-1]
        return '(' + ret + ')'


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Sequence',
           'List', 'Tuple')

#-------------------------------------------------------------------------------
