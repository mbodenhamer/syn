import six
import operator as op
from functools import wraps
from syn.base_utils import nearest_base, is_hashable, tuple_prepend, \
    get_fullname, get_mod, get_typename, AttrDict, hasmethod, import_module, \
    quote_string, iteration_length, escape_for_eval, compose, safe_vars

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

SER_IDEMPOTENT = {int, float, bool, type(None)}
SER_BUILTINS = list(vars(six.moves.builtins).values())

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
        
        # Prevent erroneous type registrations
        if self.type is object and get_typename(self) != 'Type':
            self.type = None

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

    def attrs(self, **kwargs):
        ret = sorted(safe_vars(self.obj).keys())
        return ret

    @classmethod
    def dispatch(cls, obj):
        return cls.type_dispatch(type(obj))(obj)

    @classmethod
    def deserialize_dispatch(cls, obj):
        if not isinstance(obj, dict):
            return cls.dispatch(obj)

        if SER_KEYS.name not in obj or SER_KEYS.mod not in obj:
            return cls.dispatch(obj)

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
        if not isinstance(dct, dict):
            return dct

        name = dct[SER_KEYS.name]
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
            return escape_for_eval(self.obj._estr(**kwargs))

        objstr = escape_for_eval(quote_string(str(self.obj)))
        return '{}({})'.format(get_typename(self.obj), objstr)

    def _find_ne(self, other, func, **kwargs):
        from .ne import DiffersAtAttribute, NotEqual
        for attr in self.attrs():
            if not func(getattr(self.obj, attr),
                        getattr(other, attr)):
                return DiffersAtAttribute(self.obj, other, attr)
        return NotEqual(self.obj, other)

    def find_ne(self, other, func=op.eq, **kwargs):
        if func(self.obj, other):
            return

        if type(self.obj) is not type(other):
            from .ne import DifferentTypes
            return DifferentTypes(self.obj, other)

        if hasmethod(self.obj, '_find_ne'):
            return self.obj._find_ne(other, func, **kwargs)
        return self._find_ne(other, func, **kwargs)

    @classmethod
    def _generate(cls, **kwargs):
        if hasmethod(cls.type, '_generate'):
            return cls.type._generate(**kwargs)
        raise NotImplementedError

    @classmethod
    def generate(cls, **kwargs):
        if cls.gen_type is None and cls.gen_types is None:
            return cls._generate(**kwargs)
        elif cls.gen_type:
            return cls.type(generate(cls.gen_type, **kwargs))
        return cls.type(*[generate(typ, **kwargs) for typ in cls.gen_types])

    def _hashable(self, **kwargs):
        return hashable(serialize(self.obj))

    @return_if(is_hashable)
    def hashable(self, **kwargs):
        if hasmethod(self.obj, '_hashable'):
            return self.obj._hashable(**kwargs)
        return self._hashable(**kwargs)

    def pairs(self, **kwargs):
        ret = [(attr, getattr(self.obj, attr)) for attr in self.attrs(**kwargs)]
        return ret

    def _rstr(self, **kwargs):
        return str(self.obj)

    def rstr(self, **kwargs):
        '''The idea is somethinig like a recursive str().'''
        if hasmethod(self.obj, '_rstr'):
            return self.obj._rstr(**kwargs)
        return self._rstr(**kwargs)
    
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
            dct[SER_KEYS.attrs] = serialize(dict(self.pairs(**kwargs)), **kwargs)

        return dct

    @classmethod
    def _serialize_dict(cls, typ, **kwargs):
        if typ in SER_BUILTINS:
            mod = 'six.moves.builtins'
        else:
            mod = get_mod(typ)

        return {SER_KEYS.name: get_typename(typ),
                SER_KEYS.mod: mod}

    def serialize(self, **kwargs):
        # TODO: option for custom idempotent types (may be different
        # for different serialization methods)
        if type(self.obj) in SER_IDEMPOTENT:
            return self.obj

        dct = self._serialize_dict(type(self.obj), **kwargs)
        if hasmethod(self.obj, '_serialize'):
            return self.obj._serialize(dct, **kwargs)
        
        self._serialize(dct, **kwargs)
        return dct

    @classmethod
    def serialize_type(cls, typ, **kwargs):
        dct = cls._serialize_dict(typ, **kwargs)
        dct[SER_KEYS.is_type] = True
        return dct

    def _visit(self, k, **kwargs):
        if self.is_primitive:
            return self.obj
        
        attr = self._attrs[k]
        val = getattr(self.obj, attr)
        return attr, val

    def visit(self, k, **kwargs):
        step = kwargs.get('step', 1)
        enum = kwargs.get('enumerate', False)

        self._attrs = self.attrs(**kwargs)
        self.is_primitive = not bool(self._attrs)
        N = self.visit_len(**kwargs)
            
        count = 0
        limit = iteration_length(N, k, step)
        while True:
            if count >= limit:
                raise StopIteration

            if hasmethod(self.obj, '_visit'):
                item = self.obj._visit(k, **kwargs)
            else:
                item = self._visit(k, **kwargs)

            if enum:
                yield k, item
            else:
                yield item

            k += step
            count += 1

    def _visit_len(self, **kwargs):
        if self.is_primitive:
            return 1
        return len(self._attrs)

    def visit_len(self, **kwargs):
        if hasmethod(self.obj, '_visit_len'):
            return self.obj._visit_len(**kwargs)
        return self._visit_len(**kwargs)


#-------------------------------------------------------------------------------
# TypeType


class TypeType(Type):
    type = type

    def attrs(self, **kwargs):
        return []


#-------------------------------------------------------------------------------
# Utilities

def attrs(obj, **kwargs):
    return Type.dispatch(obj).attrs(**kwargs)

def deserialize(obj, **kwargs):
    return Type.deserialize_dispatch(obj).deserialize(obj, **kwargs)

def enumerate(typ, **kwargs):
    for item in Type.type_dispatch(typ).enumerate(**kwargs):
        yield item

def estr(obj, **kwargs):
    '''Return a string that can evaluate into an equivalent object.

    NOTE: this function is experimental and not fully supported.
    '''
    return Type.dispatch(obj).estr(**kwargs)

def find_ne(a, b, func=op.eq, **kwargs):
    return Type.dispatch(a).find_ne(b, func, **kwargs)

def generate(typ, **kwargs):
    return Type.type_dispatch(typ).generate(**kwargs)

def hashable(obj, **kwargs):
    return Type.dispatch(obj).hashable(**kwargs)

def pairs(obj, **kwargs):
    return Type.dispatch(obj).pairs(**kwargs)

def rstr(obj, **kwargs):
    return Type.dispatch(obj).rstr(**kwargs)

def serialize(obj, **kwargs):
    if isinstance(obj, type):
        return Type.type_dispatch(obj).serialize_type(obj, **kwargs)
    return Type.dispatch(obj).serialize(**kwargs)

def visit(obj, k=0, **kwargs):
    for item in Type.dispatch(obj).visit(k, **kwargs):
        yield item

def safe_sorted(obj, **kwargs):
    try:
        return sorted(obj, **kwargs)
    except (TypeError, UnicodeDecodeError):
        kwargs['key'] = kwargs.get('key', compose(hash, hashable))
        return sorted(obj, **kwargs)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('TYPE_REGISTRY', 'SER_KEYS', 'Type', 'TypeType',
           'deserialize', 'enumerate', 'estr', 'find_ne', 'generate', 'attrs',
           'hashable', 'rstr', 'serialize', 'visit', 'safe_sorted', 'pairs')

#-------------------------------------------------------------------------------
