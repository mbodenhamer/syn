import six

#-------------------------------------------------------------------------------
# Type registry

TYPE_REGISTRY = {}

#-------------------------------------------------------------------------------
# TypeMeta


class TypeMeta(type):
    def __init__(self, *args):
        super(TypeMeta, self).__init__(*args)
        
        if self.type is not None:
            TYPE_REGISTRY[self.type] = self


#-------------------------------------------------------------------------------
# Type


@six.add_metaclass(TypeMeta)
class Type(object):
    type = None

    def __init__(self, obj):
        self.obj = obj

    def hashable(self):
        pass

    def istr(self):
        return str(self.obj)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Type',)

#-------------------------------------------------------------------------------
