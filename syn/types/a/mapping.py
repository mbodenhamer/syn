import collections
from .base import Type, return_
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


#-------------------------------------------------------------------------------
# Mappings

class Dict(Mapping): 
    type = dict

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
