import collections
from syn.base_utils import rand_dict
from .base import Type, return_, serialize
from .base import hashable, is_hashable
from .numeric import Int

#-------------------------------------------------------------------------------
# Mapping


class Mapping(Type):
    type = collections.Mapping

    @return_(is_hashable)
    def hashable(self, **kwargs):
        return tuple((hashable(key, **kwargs),
                      hashable(value, **kwargs))
                     for key, value in self.obj.items())
        
    def _serialize(self, dct, **kwargs):
        for key, value in self.obj.items():
            dct[serialize(key)] = serialize(value)


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
