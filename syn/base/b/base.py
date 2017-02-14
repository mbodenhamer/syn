import os
import six
from jinja2 import Template
from operator import itemgetter
from collections import Mapping
from .meta import Attrs, Meta, create_hook
from syn.base_utils import AttrDict, ReflexiveDict, message, get_mod, \
    get_typename, SeqDict, callables, istr, rgetattr, get_fullname
from syn.types import Type, pairs, estr, DiffersAtAttribute, hashable, \
    SER_KEYS, serialize

#-------------------------------------------------------------------------------
# Templates

DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(DIR, 'templates')

with open(os.path.join(TEMPLATES, 'class.j2'), 'r') as f:
    CLASS_TEMPLATE = Template(f.read())
    CLASS_TEMPLATE.environment.trim_blocks = True
    CLASS_TEMPLATE.environment.lstrip_blocks = True

#-------------------------------------------------------------------------------
# Hook Decorators

class _InitHook(object):
    '''Dummy class to ensure that callable is really an init hook.'''
    pass

class _CoerceHook(object):
    '''Dummy class to ensure that callable is really a coerce hook.'''
    pass

class _SetstateHook(object):
    '''Dummy class to ensure that callable is really a setstate hook.'''
    pass

def init_hook(f):
    f.is_init_hook = _InitHook
    return f

def coerce_hook(f):
    f.is_coerce_hook = _CoerceHook
    return f

def setstate_hook(f):
    f.is_setstate_hook = _SetstateHook
    return f

#-------------------------------------------------------------------------------
# Base


@six.add_metaclass(Meta)
class Base(object):
    _attrs = Attrs()
    _aliases = SeqDict()
    _groups = ReflexiveDict('_all',
                            '_internal',
                            'eq_exclude',
                            'hash_exclude',
                            'generate_exclude',
                            'getstate_exclude',
                            'repr_exclude',
                            'str_exclude',
                            'update_trigger')
    _opts = AttrDict(args = (),
                     autodoc = True,
                     coerce_args = False,
                     id_equality = False,
                     init_validate = False,
                     make_hashable = False,
                     make_type_object = True,
                     optional_none = False,
                     repr_template = '',
                     register_subclasses = False)
    _seq_opts = SeqDict(coerce_hooks = (),
                        init_hooks = (),
                        init_order = (),
                        create_hooks = (),
                        setstate_hooks = (),
                        metaclass_lookup = ('coerce_hooks',
                                            'init_hooks',
                                            'create_hooks',
                                            'setstate_hooks'))

    __hash__ = None

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

        for attr, val in kwargs.items():
            setattr(self, attr, val)

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
    def _generate_documentation_signature(cls, attrs):
        sig = get_typename(cls) + '('

        strs = []
        for attr in attrs:
            obj = cls._attrs[attr]
            s = attr
            if obj.default:
                s += '=' + str(obj.default)
            if obj.optional:
                s = '[' + s + ']'
            strs.append(s)
        strs.append('**kwargs')

        sig += ', '.join(strs)
        sig += ')'
        return sig

    @classmethod
    def _generate_documentation_attrspec(cls, attrs):
        specs = []
        for attr in attrs:
            obj = cls._attrs[attr]
            spec = attr
            if obj.optional:
                spec += ' [**Optional**]'
            if obj.default is not None:
                spec += ' (*default* = {})'.format(obj.default)
            
            spec += ': {}'.format(obj.type.rst())
            if obj.doc:
                spec += '\n    '
                spec += obj.doc
            specs.append(spec)

        return '\n'.join(specs)

    @classmethod
    def _generate_documentation_optspec(cls):
        specs = []
        for opt, val in sorted(cls._opts.items(), key=itemgetter(0)):
            specs.append('* {}: {}'.format(opt, val))
        for opt, val in sorted(cls._seq_opts.items(), key=itemgetter(0)):
            specs.append('* {}: {}'.format(opt, val))

        return '\n'.join(specs)

    @classmethod
    def _generate_documentation_aliasspec(cls):
        specs = []
        for attr, als in cls._aliases.items():
            specs.append('* {}: {}'.format(attr, ', '.join(als)))

        return '\n'.join(specs)

    @classmethod
    def _generate_documentation_groupspec(cls):
        specs = []
        for attr, group in cls._groups.items():
            if group:
                specs.append('* {}: {}'.format(attr, ', '.join(sorted(group))))

        return '\n'.join(specs)

    @classmethod
    @create_hook
    def _generate_documentation(cls):
        if not cls._get_opt('autodoc', default=True):
            return

        if rgetattr(cls, '__init__.__func__', False) is False:
            return
        args = cls._get_opt('args', default=())
        kw_attrs = cls._data.kw_attrs

        data = {}
        data['signature'] = cls._generate_documentation_signature(args)
        data['doc'] = cls.__doc__ if cls.__doc__ else ''
        if cls.__init__.__func__.__doc__:
            data['doc'] += '\n\n' + cls.__init__.__func__.__doc__
        data['attrspec'] = cls._generate_documentation_attrspec(args)
        data['kwattrspec'] = cls._generate_documentation_attrspec(kw_attrs)
        data['optspec'] = cls._generate_documentation_optspec()
        data['aliasspec'] = cls._generate_documentation_aliasspec()
        data['groupspec'] = cls._generate_documentation_groupspec()

        doc = CLASS_TEMPLATE.render(data)
        cls.__doc__ = doc

    @classmethod
    def _find_hooks(cls, hook_attr, hook_type):
        funcs = callables(cls)
        return [f for f in funcs.values() 
                if getattr(f, hook_attr, None) is hook_type]

    @classmethod
    @create_hook
    def _create_init_hooks(cls):
        hooks = cls._find_hooks('is_init_hook', _InitHook)
        cls._data.init_hooks = list(cls._data.init_hooks) + hooks

    @classmethod
    @create_hook
    def _create_coerce_hooks(cls):
        hooks = cls._find_hooks('is_coerce_hook', _CoerceHook)
        cls._data.coerce_hooks = list(cls._data.coerce_hooks) + hooks

    @classmethod
    @create_hook
    def _create_setstate_hooks(cls):
        hooks = cls._find_hooks('is_setstate_hook', _SetstateHook)
        cls._data.setstate_hooks = list(cls._data.setstate_hooks) + hooks

    @classmethod
    @create_hook
    def _make_type_object(cls):
        if cls._class_data.clsname == 'Base' or not cls._opts.make_type_object:
            return

        class BaseChildGeneratedType(BaseType):
            type = cls

    def __getstate__(self):
        return self.to_dict(exclude=['getstate_exclude'])

    def __setstate__(self, state):
        for attr, val in state.items():
            setattr(self, attr, val)

        if self._data.setstate_hooks:
            for hook in self._data.setstate_hooks:
                hook(self)

    def __eq__(self, other):
        if self._opts.id_equality:
            return self is other

        if type(self) is not type(other):
            return False

        dct1 = self.to_dict(exclude=['eq_exclude'])
        dct2 = other.to_dict(exclude=['eq_exclude'])
        return dct1 == dct2

    def __ne__(self, other):
        return not (self == other)

    def _repr_template(self):
        dct = self.to_dict()
        dct['__name__'] = get_typename(self)
        dct['__mod__'] = get_mod(self)

        template = self._opts.repr_template
        return template.format(**dct)

    def __repr__(self):
        if self._opts.repr_template:
            return self._repr_template()

        out = '<' + get_mod(self) + '.' + get_typename(self) + ' '
        out += str(self.to_dict(exclude=['repr_exclude']))
        out += '>'
        return out

    def __str__(self):
        return self.istr()

    def _istr_attrs(self, base, pretty, indent):
        strs = []
        attrs = self.to_dict(exclude=['str_exclude'])
        for attr, val in sorted(attrs.items(), 
                                key=lambda x: \
                                self._data.attr_display_order.index(x[0])):
            start = '{} = '.format(attr)
            val_indent = indent + len(start)
            tmp = start + istr(val, pretty, val_indent)
            strs.append(tmp)
        return base.join(strs)

    def istr(self, pretty=False, indent=0):
        '''Returns a string that, if evaluated, produces an equivalent object.'''
        ret = '{}('.format(get_typename(self))
        base = ','
        if pretty:
            indent += len(ret)
            base += '\n' + ' ' * indent
        else:
            base += ' '

        ret += self._istr_attrs(base, pretty, indent) + ')'
        return ret
        
    def pretty(self, indent=0):
        '''Returns a pretty-printed version if istr().'''
        return self.istr(pretty=True, indent=indent)

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
    def _enumeration_value(cls, x, **kwargs):
        kwargs = {}
        for attr, typ in cls._attrs.types.items():
            if attr in cls._groups.generate_exclude:
                continue
            kwargs[attr] = typ.enumeration_value(x, **kwargs)
        return cls(**kwargs)

    def _estr(self, **kwargs):
        kwargs = {attr: estr(val) for attr, val in pairs(self, **kwargs)}
        argstr = ','.join('{}={}'.format(attr, val) for attr, val in kwargs.items())
        return '{}({})'.format(get_typename(self), argstr)

    def _find_ne(self, other, func, **kwargs):
        for attr, value in pairs(self, exclude=['eq_exclude']):
            if not func(value, getattr(other, attr)):
                return DiffersAtAttribute(self, other, attr)

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

    @classmethod
    def _generate(cls, **kwargs):
        kwargs = {}
        for attr, typ in cls._attrs.types.items():
            if attr in cls._groups.generate_exclude:
                continue
            kwargs[attr] = typ.generate(**kwargs)
        return cls(**kwargs)

    def _hashable(self, **kwargs):
        items = [hashable(val, **kwargs) for val in self.to_tuple(exclude=['hash_exclude'])]
        items.insert(0, get_fullname(self))
        return tuple(items)

    def _serialize(self, dct, **kwargs):
        kwargs = dict(kwargs)
        exclude = list(kwargs.get('exclude', []))
        if 'getstate_exclude' not in exclude:
            exclude += ['getstate_exclude']
        kwargs['exclude'] = exclude
        dct[SER_KEYS.kwargs] = {attr: serialize(value, **kwargs)
                                for attr, value in pairs(self, **kwargs)}
        return dct

    def to_dict(self, **kwargs):
        '''Convert the object into a dict of its declared attributes.
        
        May exclude certain attribute groups by listing them in exclude=[].
        
        May include certain attribute groups (to the exclusion of all others) by listing them in include=[].
        '''
        return dict(pairs(self, **kwargs))

    def to_tuple(self, **kwargs):
        '''Convert the object into a tuple of its declared attribute values.
        '''
        values = [val for attr, val in pairs(self, **kwargs)]
        return tuple(values)

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
# Type Registration


class BaseType(Type):
    type = Base

    def attrs(self, **kwargs):
        exclude = kwargs.get('exclude', [])
        include = kwargs.get('include', [])

        if include and exclude:
            raise TypeError('Cannot specify both include and exclude')

        if exclude:
            exclude = self.obj._groups.union(*exclude)
        else:
            exclude = set()

        if include:
            exclude = self.obj._groups.complement(*include)

        return sorted(attr for attr in self.obj._attrs.types
                      if attr not in exclude and hasattr(self.obj, attr))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Base', 'BaseType', 'init_hook', 'coerce_hook', 'setstate_hook')

#-------------------------------------------------------------------------------
