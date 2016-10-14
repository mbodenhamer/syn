import collections
from syn.base_utils import rand_dict, get_fullname, tuple_prepend
from .base import Type, serialize, hashable
from .numeric import Int

#-------------------------------------------------------------------------------
# Mapping


class Mapping(Type):
    type = collections.Mapping

    def _hashable(self, **kwargs):
        tup = tuple((hashable(key, **kwargs),
                     hashable(value, **kwargs))
                    for key, value in self.obj.items())
        return tuple_prepend(get_fullname(self.obj), tup)

    def _serialize(self, dct, **kwargs):
        for key, value in self.obj.items():
            dct[key] = serialize(value)


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
