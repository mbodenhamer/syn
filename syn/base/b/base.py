import six
from .meta import Attrs, Meta
from syn.base_utils import AttrDict, ReflexiveDict

#-------------------------------------------------------------------------------
# Base


#import pdb; pdb.set_trace()
@six.add_metaclass(Meta)
class Base(object):
    _attrs = Attrs()
    _groups = ReflexiveDict('eq_exclude',
                            'repr_exclude')
    _opts = AttrDict(args = (),
                     coerce_args = False,
                     id_equality = False,
                     init_validate = False,
                     optional_none = False)

    @classmethod
    def groups_enum(cls):
        return ReflexiveDict(cls._groups)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Base',)

#-------------------------------------------------------------------------------
