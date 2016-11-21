import collections
from syn.base_utils import rand_dict, get_fullname, tuple_prepend, \
    get_typename, escape_for_eval
from .base import Type, serialize, hashable, rstr, estr, SER_KEYS, deserialize
from .numeric import Int
from .sequence import list_enumval
from .set import set_enumval
from .ne import Value
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
        return dict_enumval(x, **kwargs)

    def estr(self, **kwargs):
        parts = ["{}: {}".format(estr(key, **kwargs), estr(value, **kwargs))
                 for key, value in self.obj.items()]
        ret = '{' + ', '.join(parts) + '}'
        ret = '{}({})'.format(get_typename(self.obj), ret)
        return escape_for_eval(ret)

    def _find_ne(self, other, **kwargs):
        # TODO: return FindNE object here
        keys = set(self.obj.keys())
        okeys = set(other.keys())

        if keys != okeys:
            diffs = keys.difference(okeys).union(okeys.difference(keys))
            return Value('key differences: {}'.format(rstr(diffs)))

        for key, value in self.obj.items():
            oval = other[key]
            if value != oval:
                return Value('key {}: {} != {}'.format(key, value, oval))

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
        # Don't use the buffer if you are modifying the mapping in between
        # _visit calls
        use_buffer = kwargs.get('use_buffer', True)
        if use_buffer:
            N = len(self.visit_buffer)
            if 0 <= k < N:
                key = self.visit_buffer[k]
            else:
                idx_diff = k - (N - 1)
                for item in islice(self.visit_iter, idx_diff):
                    self.visit_buffer.append(item)
                key = self.visit_buffer[k]
        else:
            keys = list(self.obj)
            key = keys[k]

        return key, self.obj[key]

    def _visit_len(self, **kwargs):
        return len(self.obj)


#-------------------------------------------------------------------------------
# Mappings


class Dict(Mapping): 
    type = dict

    @classmethod
    def _generate(cls, **kwargs):
        return rand_dict(**kwargs)


class OrderedDict(Dict): 
    type = collections.OrderedDict
    gen_type = Dict


class DefaultDict(Dict): 
    type = collections.defaultdict
    gen_types = (Int, Dict)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Mapping',
           'Dict', 'DefaultDict', 'OrderedDict')

#-------------------------------------------------------------------------------
