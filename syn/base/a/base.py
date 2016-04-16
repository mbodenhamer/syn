import six
from .meta import Attrs, Meta
from syn.base_utils import AttrDict

#-------------------------------------------------------------------------------
# Base


@six.add_metaclass(Meta)
class Base(object):
    _attrs = Attrs()
    _opts = AttrDict()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Base',)

#-------------------------------------------------------------------------------
