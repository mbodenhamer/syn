from itertools import islice
from syn.base_utils import get_fullname, rand_set, rand_frozenset, \
    escape_for_eval, get_typename
from .base import Type, hashable, serialize, SER_KEYS, rstr, estr, safe_sorted
from syn.base_utils.rand import HASHABLE_TYPES
from .sequence import list_enumval
from .ne import SetDifferences

#-------------------------------------------------------------------------------
# Utilities

def set_enumval(x, **kwargs):
    kwargs['types'] = kwargs.get('types', HASHABLE_TYPES)
    return set(list_enumval(x, **kwargs))

#-------------------------------------------------------------------------------
# Set


class Set(Type):
    type = set

    def __init__(self, *args, **kwargs):
        super(Set, self).__init__(*args, **kwargs)
        self.visit_buffer = []
        self.visit_iter = iter(self.obj)

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return set_enumval(x, **kwargs)

    def estr(self, **kwargs):
        parts = [estr(item, **kwargs) for item in self.obj]
        ret = '[' + ', '.join(parts) + ']'
        ret = '{}({})'.format(get_typename(self.obj), ret)
        return escape_for_eval(ret)

    def _find_ne(self, other, func, **kwargs):
        return SetDifferences(self.obj, other)

    @classmethod
    def _generate(cls, **kwargs):
        return rand_set(**kwargs)

    def _rstr(self, **kwargs):
        # TODO: add pretty option
        parts = [rstr(item, **kwargs) for item in self.obj]
        ret = '{' + ', '.join(parts) + '}'
        return ret

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [[serialize(item, **kwargs) for item in self.obj]]

    def _visit(self, k, **kwargs):
        if not self.visit_buffer:
            self.visit_buffer = safe_sorted(list(self.obj))
        return self.visit_buffer[k]

    def _visit_len(self, **kwargs):
        return len(self.obj)


#-------------------------------------------------------------------------------
# FrozenSet


class FrozenSet(Set):
    type = frozenset

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return frozenset(super(FrozenSet, cls)._enumeration_value(x, **kwargs))

    @classmethod
    def _generate(cls, **kwargs):
        return rand_frozenset(**kwargs)

    def _rstr(self, **kwargs):
        ret = super(FrozenSet, self)._rstr(**kwargs)
        return 'frozenset(' + ret + ')'


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Set', 'FrozenSet')

#-------------------------------------------------------------------------------
