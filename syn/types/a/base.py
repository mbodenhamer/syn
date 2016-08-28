import six
from functools import wraps
from syn.type.a import Type as Type_
from syn.base_utils import nearest_base, is_hashable, tuple_prepend, \
    get_fullname

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
            self.type_ = Type_.dispatch(self.type)


#-------------------------------------------------------------------------------
# Type


@six.add_metaclass(TypeMeta)
class Type(object):
    type = object
    gen_type = None
    gen_types = None

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def dispatch(cls, obj):
        typ = type(obj)
        if typ in TYPE_REGISTRY:
            return TYPE_REGISTRY[typ](obj)

        base = nearest_base(typ, TYPE_REGISTRY.keys())
        return TYPE_REGISTRY[base](obj)

    @classmethod
    def generate(cls, **kwargs):
        if cls.gen_type is None and cls.gen_types is None:
            return cls.type_.generate(**kwargs)
        elif cls.gen_type:
            return cls.type(cls.gen_type.generate(**kwargs))
        return cls.type(typ.generate(**kwargs) for typ in cls.gen_types)

    @return_(is_hashable)
    def hashable(self):
        return tuple_prepend(get_fullname(self.obj),
                             hashable(self.obj.__dict__))

    def istr(self):
        return str(self.obj)


#-------------------------------------------------------------------------------
# Utilities

def hashable(obj):
    return Type.dispatch(obj).hashable()

#-------------------------------------------------------------------------------
# __all__

__all__ = ('TYPE_REGISTRY', 'Type',
           'hashable')

#-------------------------------------------------------------------------------
