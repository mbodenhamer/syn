import six
from collections import Mapping
from .meta import Attrs, Meta
from syn.base_utils import (AttrDict, ReflexiveDict, message, get_mod,
                            get_typename, SeqDict, callables)

#-------------------------------------------------------------------------------
# Hook Decorators

def init_hook(f):
    f.init_hook = True
    return f

def coerce_hook(f):
    f.coerce_hook = True
    return f

def create_hook(f):
    f.create_hook = True
    return f

#-------------------------------------------------------------------------------
# Base


@six.add_metaclass(Meta)
class Base(object):
    _attrs = Attrs()
    _groups = ReflexiveDict('_all',
                            '_internal',
                            'eq_exclude',
                            'getstate_exclude',
                            'repr_exclude',
                            'update_trigger')
    _opts = AttrDict(args = (),
                     coerce_args = False,
                     id_equality = False,
                     init_validate = False,
                     optional_none = False)
    _seq_opts = SeqDict(coerce_hooks = (),
                        init_hooks = (),
                        init_order = (),
                        create_hooks = (),
                        metaclass_lookup = ('coerce_hooks',
                                            'init_hooks',
                                            'create_hooks'))

    def __init__(self, *args, **kwargs):
        _args = self._opts.args

        for key in self._attrs.defaults:
            if key in _args:
                if len(args) > _args.index(key):
                    continue # This value has been supplied as a non-kw arg
            if key not in kwargs:
                kwargs[key] = self._attrs.defaults[key]
        
        if _args:
            if len(args) > len(_args):
                raise TypeError('__init__ takes up to {} positional arguments '
                                '({} given)'.format(len(_args), len(args)))

            for k, arg in enumerate(args):
                key = _args[k]
                if key in kwargs:
                    raise TypeError('__init__ got multiple values for argument '
                                    '{}'.format(key))
                kwargs[_args[k]] = arg

        if self._opts.coerce_args:
            for key, value in list(kwargs.items()):
                typ = self._attrs.types[key]
                if not typ.query(value):
                    kwargs[key] = typ.coerce(value)

        if self._opts.optional_none:
            for attr in self._attrs.optional:
                if attr not in kwargs:
                    kwargs[attr] = None

        if self._attrs.call:
            for attr, call in self._attrs.call.items():
                value = kwargs.get(attr, None)
                if value is None:
                    kwargs[attr] = call()
                else:
                    kwargs[attr] = call(value)

        self.__setstate__(kwargs)

        if self._seq_opts.init_order:
            for attr in self._seq_opts.init_order:
                if not hasattr(self, attr):
                    setattr(self, attr, self._attrs.init[attr](self))

        if self._attrs.init:
            for attr in (set(self._attrs.init) - 
                         set(self._seq_opts.init_order)):
                if not hasattr(self, attr):
                    setattr(self, attr, self._attrs.init[attr](self))

        if self._data.init_hooks:
            for hook in self._data.init_hooks:
                hook(self)

        if self._opts.init_validate:
            self.validate()

    @classmethod
    def _find_hooks(cls, hook_attr):
        funcs = callables(cls)
        return [f for f in funcs.values() if getattr(f, hook_attr, False)]

    @classmethod
    @create_hook
    def _create_init_hooks(cls):
        hooks = cls._find_hooks('init_hook')
        if cls._data.init_hooks:
            cls._data.init_hooks = list(cls._data.init_hooks) + hooks
        else:
            cls._data.init_hooks = hooks

    @classmethod
    @create_hook
    def _create_coerce_hooks(cls):
        hooks = cls._find_hooks('coerce_hook')
        if cls._data.coerce_hooks:
            cls._data.coerce_hooks = list(cls._data.coerce_hooks) + hooks
        else:
            cls._data.coerce_hooks = hooks

    def __getstate__(self):
        return self.to_dict('getstate_exclude')

    def __setstate__(self, state):
        for attr, val in state.items():
            setattr(self, attr, val)

    def __eq__(self, other):
        if self._opts.id_equality:
            return self is other

        if type(self) is not type(other):
            return False

        dct1 = self.to_dict()
        dct2 = other.to_dict()
        return dct1 == dct2

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        out = '<' + get_mod(self) + '.' + get_typename(self) + ' '
        out += str(self.to_dict('repr_exclude'))
        out += '>'
        return out

    @classmethod
    def _dict_from_mapping(cls, value):
        return dict(value)

    @classmethod
    def _dict_from_object(cls, obj):
        return {attr: getattr(obj, attr) for attr in cls._attrs.types
                if hasattr(obj, attr)}

    @classmethod
    def _dict_from_sequence(cls, seq):
        return {cls._opts.args[k]: val for k, val in enumerate(seq)}

    @classmethod
    def coerce(cls, value):
        if isinstance(value, Mapping):
            dct = cls._dict_from_mapping(value)
        else:
            return cls(value)

        if cls._data.coerce_hooks:
            for hook in cls._data.coerce_hooks:
                hook(dct)

        if cls._opts.coerce_args:
            return cls(**dct)

        types = cls._attrs.types
        attrs = {attr: types[attr].coerce(val) 
                 for attr, val in dct.items()}
        return cls(**attrs)

    @classmethod
    def from_mapping(cls, value):
        return cls(**cls._dict_from_mapping(value))

    @classmethod
    def from_object(cls, obj):
        return cls(**cls._dict_from_object(obj))

    @classmethod
    def from_sequence(cls, seq):
        if len(seq) > len(cls._opts.args):
            raise ValueError("More elements in sequence than in object "
                             "positional args")
        return cls(**cls._dict_from_sequence(seq))

    def to_dict(self, *groups, **kwargs):
        '''Convert the object into a dict of its declared attributes.
        
        May exclude certain attribute groups by listing them in *groups.
        
        May include certain attribute groups (to the exclusion of all others) by listing them in *groups and supplying the include=True keyword argument.
        '''
        include = kwargs.get('include', False)

        if not include:
            if groups:
                exclude = self._groups.union(*groups)
            else:
                exclude = set()
        else:
            exclude = self._groups.complement(*groups)

        return {attr: getattr(self, attr) for attr in self._attrs.types
                if attr not in exclude and hasattr(self, attr)}

    def validate(self):
        '''Raise an exception if the object is missing required attributes, or if the attributes are of an invalid type.
        '''
        optional = self._attrs.optional
        optional_none = self._opts.optional_none

        for attr, typ in self._attrs.types.items():
            if not hasattr(self, attr):
                if attr in optional:
                    continue
                raise AttributeError('Required attribute {} not defined'.
                                     format(attr))

            val = getattr(self, attr)
            if optional_none:
                if attr in optional and val is None:
                    continue

            res, e = typ.query_exception(val)
            if not res:
                raise TypeError('Validation error for attribute {}: {}'.
                                format(attr, message(e)))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Base', 'init_hook', 'coerce_hook', 'create_hook')

#-------------------------------------------------------------------------------
