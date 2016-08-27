import six
from functools import wraps
from syn.base_utils import nearest_base, is_hashable

#-------------------------------------------------------------------------------
# Type registry

TYPE_REGISTRY = {}

#-------------------------------------------------------------------------------
# Utilities

class return_(object):
    def __init__(self, check_func):
        self.check_func = check_func

    def __call__(self, f):
        @wraps(f)
        def func(self_):
            if self.check_func(self_.obj):
                return self_.obj
            return f(self_)
        return func

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
    type = object

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def dispatch(cls, obj):
        return TYPE_REGISTRY[nearest_base(type(obj), TYPE_REGISTRY.keys())]

    @return_(is_hashable)
    def hashable(self):
        raise NotImplementedError

    def istr(self):
        return str(self.obj)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Type',)

#-------------------------------------------------------------------------------
