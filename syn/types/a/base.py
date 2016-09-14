import six
from functools import wraps
from syn.base_utils import nearest_base, is_hashable, tuple_prepend, \
    get_fullname, get_mod, get_typename, AttrDict, hasmethod, import_module

#-------------------------------------------------------------------------------
# Type registry

TYPE_REGISTRY = {}

#-------------------------------------------------------------------------------
# Serialization Information

SER_KEYS = AttrDict(name = '___name',
                    mod = '___mod',
                    args = '___args',
                    kwargs = '___kwargs',
                    attrs = '___attrs',
                    is_type = '___is_type')

SER_IDEMPOTENT = {int, float, bool, str}
SER_BUILTINS = vars(six.moves.builtins)

#-------------------------------------------------------------------------------
# Utilities

class return_if(object):
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
        
        # Register type
        if self.type is not None:
            TYPE_REGISTRY[self.type] = self

        # Populate ser_kwargmap as needed
        if self.ser_kwargs and not self.ser_kwargmap:
            for kwarg in self.ser_kwargs:
                if kwarg not in self.ser_kwargmap.values():
                    self.ser_kwargmap[kwarg] = kwarg


#-------------------------------------------------------------------------------
# Type


@six.add_metaclass(TypeMeta)
class Type(object):
    type = object
    gen_type = None
    gen_types = None

    ser_args = ()
    ser_kwargs = ()
    ser_kwargmap = {} # kwarg: attr
    ser_attrs = None

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def dispatch(cls, obj):
        return cls.type_dispatch(type(obj))(obj)

    @classmethod
    def deserialize_dispatch(cls, obj):
        if not isinstance(obj, dict):
            if isinstance(obj, type):
                return cls.type_dispatch(obj)
            return cls.dispatch(obj)

        if SER_KEYS.name not in obj or SER_KEYS.mod not in obj:
            return cls.dispatch(obj)

        # mod = __import__(obj[SER_KEYS.mod], fromlist=[obj[SER_KEYS.name]])
        mod = import_module(obj[SER_KEYS.mod])
        return cls.type_dispatch(getattr(mod, obj[SER_KEYS.name]))

    @classmethod
    def type_dispatch(cls, typ):
        if typ in TYPE_REGISTRY:
            return TYPE_REGISTRY[typ]

        base = nearest_base(typ, TYPE_REGISTRY.keys())
        ret = TYPE_REGISTRY[base]
        TYPE_REGISTRY[typ] = ret # cache the result to avoid future searches
        return ret

    @classmethod
    def deserialize(cls, dct, **kwargs_):
        name = dct[SER_KEYS.name]
        # mod = __import__(dct[SER_KEYS.mod], fromlist=[name])
        mod = import_module(dct[SER_KEYS.mod])
        args = dct.get(SER_KEYS.args, [])
        kwargs = dct.get(SER_KEYS.kwargs, {})
        attrs = dct.get(SER_KEYS.attrs, {})

        if args:
            args = deserialize(args, **kwargs_)
        if kwargs:
            kwargs = deserialize(kwargs, **kwargs_)
        if attrs:
            attrs = deserialize(attrs, **kwargs_)

        typ = getattr(mod, name)
        if dct.get(SER_KEYS.is_type, False):
            return typ

        if args and kwargs:
            obj = typ(*args, **kwargs)
        elif args:
            obj = typ(*args)
        elif kwargs:
            obj = typ(**kwargs)
        else:
            obj = typ()

        for attr, val in attrs.items():
            setattr(obj, attr, val)

        if hasmethod(obj, '_deserialize'):
            obj._deserialize(dct)
        return obj

    @classmethod
    def enumerate(cls, **kwargs):
        start = kwargs.get('start', 0)
        step = kwargs.get('step', 1)
        max_enum = kwargs.get('max_enum', None)

        k = 0
        x = start
        while True:
            if k >= max_enum:
                break
            yield cls.enumeration_value(x, **kwargs)
            x += step
            k += 1

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        raise NotImplementedError

    @classmethod
    def enumeration_value(cls, x, **kwargs):
        if hasmethod(cls.type, '_enumeration_value'):
            return cls.type._enumeration_value(x, **kwargs)
        return cls._enumeration_value(x, **kwargs)

    def estr(self, **kwargs):
        '''Should return a string that can eval into an equivalent object'''
        if hasmethod(self.obj, '_estr'):
            return self.obj._estr(**kwargs)
        return str(self.obj)

    @classmethod
    def _generate(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def generate(cls, **kwargs):
        if cls.gen_type is None and cls.gen_types is None:
            return cls._generate(**kwargs)
        elif cls.gen_type:
            return cls.type(cls.gen_type.generate(**kwargs))
        return cls.type(typ.generate(**kwargs) for typ in cls.gen_types)

    def _hashable(self, **kwargs):
        return hashable(serialize(self.obj))

    @return_if(is_hashable)
    def hashable(self, **kwargs):
        if hasmethod(self.obj, '_hashable'):
            return self.obj._hashable(**kwargs)
        return self._hashable(**kwargs)

    def rstr(self, **kwargs):
        '''The idea is somethinig like a recursive str().'''
        if hasmethod(self.obj, '_rstr'):
            return self.obj._rstr(**kwargs)
        return str(self.obj)

    def _serialize_dict(self, **kwargs):
        if type(self.obj) in SER_BUILTINS:
            mod = 'six.moves.builtins'
        else:
            mod = get_mod(self.obj)

        return {SER_KEYS.name: get_typename(self.obj),
                SER_KEYS.mod: mod}

    def serialize_type(self, **kwargs):
        dct = self._serialize_dict(**kwargs)
        dct[SER_KEYS.is_type] = True
        return dct

    def _serialize(self, dct, **kwargs):
        if (self.ser_args or self.ser_kwargs) and self.ser_attrs is None:
            ser_attrs = False
        elif self.ser_attrs is None:
            ser_attrs = True
        else:
            ser_attrs = bool(self.ser_attrs)

        if self.ser_args:
            dct[SER_KEYS.args] = serialize([getattr(self.obj, arg)
                                            for arg in self.ser_args])
        if self.ser_kwargs:
            dct[SER_KEYS.kwargs] = \
                serialize({kwarg: getattr(self.obj, self.ser_kwargmap[kwarg]) 
                           for kwarg in self.ser_kwargs})
        if ser_attrs:
            dct[SER_KEYS.attrs] = serialize(self.obj.__dict__, **kwargs)

        return dct

    def serialize(self, **kwargs):
        if type(self.obj) in SER_IDEMPOTENT:
            return self.obj

        dct = self._serialize_dict(**kwargs)
        if hasmethod(self.obj, '_serialize'):
            return self.obj._serialize(dct, **kwargs)
        
        self._serialize(dct, **kwargs)
        return dct

#-------------------------------------------------------------------------------
# Utilities

def deserialize(obj, **kwargs):
    return Type.deserialize_dispatch(obj).deserialize(**kwargs)

def enumerate_(obj, **kwargs):
    for item in Type.type_dispatch(obj).enumerate(**kwargs):
        yield item

def estr(obj, **kwargs):
    return Type.dispatch(obj).estr(**kwargs)

def generate(typ, **kwargs):
    return Type.type_dispatch(typ).generate(**kwargs)

def hashable(obj, **kwargs):
    return Type.dispatch(obj).hashable(**kwargs)

def rstr(obj, **kwargs):
    return Type.dispatch(obj).rstr(**kwargs)

def serialize(obj, **kwargs):
    if isinstance(obj, type):
        return Type.type_dispatch(obj).serialize_type(**kwargs)
    return Type.dispatch(obj).serialize(**kwargs)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('TYPE_REGISTRY', 'Type',
           'deserialize', 'enumerate_', 'estr', 'generate', 'hashable', 
           'rstr', 'serialize')

#-------------------------------------------------------------------------------
