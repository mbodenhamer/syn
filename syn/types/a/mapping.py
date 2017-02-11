import collections
from syn.base_utils import rand_dict, get_fullname, tuple_prepend, \
    get_typename, escape_for_eval
from .base import Type, serialize, hashable, rstr, estr, SER_KEYS, \
    deserialize, safe_sorted
from .numeric import Int
from .sequence import list_enumval
from .set import set_enumval
from .ne import KeyDifferences, DiffersAtKey
from itertools import islice

#-------------------------------------------------------------------------------
# Utilities

def dict_enumval(x, **kwargs):
    keys = list(set_enumval(x, **kwargs))
    values = list_enumval(x, **kwargs)
    N = min(len(keys), len(values))
    return dict(zip(keys[:N], values[:N]))

#-------------------------------------------------------------------------------
# Mapping


class Mapping(Type):
    type = collections.Mapping

    def __init__(self, *args, **kwargs):
        super(Mapping, self).__init__(*args, **kwargs)
        self.visit_buffer = []
        self.visit_iter = iter(self.obj)

    @classmethod
    def deserialize(cls, dct, **kwargs):
        # TODO: may need to have a special case if args or kwars is set (like for defaultdict)
        for key in SER_KEYS.values():
            if key in dct:
                del dct[key]

        ret = {key: deserialize(value, **kwargs) for key, value in dct.items()}
        return cls.type(ret)

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return cls.type(dict_enumval(x, **kwargs))

    def estr(self, **kwargs):
        parts = ["{}: {}".format(estr(key, **kwargs), estr(value, **kwargs))
                 for key, value in self.obj.items()]
        ret = '{' + ', '.join(parts) + '}'
        ret = '{}({})'.format(get_typename(self.obj), ret)
        return escape_for_eval(ret)

    def _find_ne(self, other, func, **kwargs):
        for key, value in self.obj.items():
            if key not in other:
                return KeyDifferences(self.obj, other)
            oval = other[key]
            if not func(value, oval):
                return DiffersAtKey(self.obj, other, key)
        return KeyDifferences(self.obj, other)

    def _hashable(self, **kwargs):
        tup = tuple((hashable(key, **kwargs),
                     hashable(value, **kwargs))
                    for key, value in self.obj.items())
        return tuple_prepend(get_fullname(self.obj), tup)

    def _rstr(self, **kwargs):
        # TODO: add pretty option
        parts = ["{}: {}".format(rstr(key, **kwargs), rstr(value, **kwargs))
                 for key, value in self.obj.items()]
        ret = '{' + ', '.join(parts) + '}'
        return ret

    def _serialize(self, dct, **kwargs):
        for key, value in self.obj.items():
            dct[key] = serialize(value)

    def _visit(self, k, **kwargs):
        if not self.visit_buffer:
            self.visit_buffer = safe_sorted(list(self.obj.items()))
        return self.visit_buffer[k]

    def _visit_len(self, **kwargs):
        return len(self.obj)


#-------------------------------------------------------------------------------
# Mappings


class Dict(Mapping): 
    type = dict

    @classmethod
    def _generate(cls, **kwargs):
        return rand_dict(**kwargs)

# NOTE: we don't need these right now; when we do, they can be implemented

# class OrderedDict(Dict): 
#     type = collections.OrderedDict
#     gen_type = dict


# class DefaultDict(Dict): 
#     type = collections.defaultdict
#     gen_types = (int, dict)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Mapping',
           'Dict',)

#-------------------------------------------------------------------------------
