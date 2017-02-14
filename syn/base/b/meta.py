from collections import defaultdict
from syn.five import STR
from syn.base.a import Base
from syn.type.a import Type, This
from syn.type.a.ext import Callable, Sequence
from syn.base_utils import GroupDict, AttrDict, SeqDict, ReflexiveDict,\
    callables, rgetattr, hasmethod
from functools import partial
from syn.types import hashable

from syn.base.a.meta import Attr as _Attr
from syn.base.a.meta import Attrs as _Attrs
from syn.base.a.meta import Meta as _Meta
from syn.base.a.meta import combine

_OAttr = partial(_Attr, optional=True)

#-------------------------------------------------------------------------------
# Attr attrs

attr_attrs = \
dict(type = _OAttr(None, doc='Type of the attribute'),
     default = _OAttr(None, doc='Default value of the attribute'),
     doc = _Attr(STR, '', doc='Attribute docstring'),
     optional = _Attr(bool, False, 'If true, the attribute may be omitted'),
     call = _OAttr(Callable, doc='Will be called on the value supplied '
                   'for initialization.  If no value is supplied, will be '
                   'called on the default (if given), othewise with no arguments'),
     group = _OAttr(STR, doc='Name of the group this attribute belongs to'),
     groups = _OAttr(Sequence(STR), doc='Groups this attribute beongs to'),
     internal = _Attr(bool, False, 'Not treated as a constructor argument'),
     init = _OAttr(Callable, doc='Will be called with the object as the only '
                   'parameter for initializing the attribute'),
    )

#-------------------------------------------------------------------------------
# Create Hook

class _CreateHook(object):
    '''Dummy class to ensure that callable is really a create hook.'''
    pass

def create_hook(f):
    f.is_create_hook = _CreateHook
    return f

#-------------------------------------------------------------------------------
# Data Object (for metaclass-populated values)


class Data(object):
    def __getattr__(self, attr):
        return list()


#-------------------------------------------------------------------------------
# Attr


class Attr(Base):
    _opts = dict(optional_none = True,
                 args = ('type', 'default', 'doc'))
    _attrs = attr_attrs

    def __init__(self, *args, **kwargs):
        super(Attr, self).__init__(*args, **kwargs)
        self.type = Type.dispatch(self.type)
        self.validate()


#-------------------------------------------------------------------------------
# Object Attrs Bookkeeping


class Attrs(_Attrs):
    def _update(self):
        super(Attrs, self)._update()
        self.call = {attr: spec.call for attr, spec in self.items() 
                     if spec.call is not None}
        self.internal = {attr for attr, spec in self.items() if spec.internal}

        # Process attr groups
        self.groups = defaultdict(set)
        for attr, spec in self.items():
            groups = [spec.group] if spec.group else []
            if spec.groups:
                groups.extend(list(spec.groups))
            for group in groups:
                self.groups[group].add(attr)
        self.groups = GroupDict(self.groups)


#-------------------------------------------------------------------------------
# Metaclass


class Meta(_Meta):
    _metaclass_opts = AttrDict(attrs_type = Attrs,
                               aliases_type = SeqDict,
                               opts_type = AttrDict,
                               seq_opts_type = SeqDict)

    def __init__(self, clsname, bases, dct):
        super(Meta, self).__init__(clsname, bases, dct)

        self._set_hash()
        self._populate_data()
        self._combine_groups()
        self._process_create_hooks()

    def _get_opt(self, name='', default=None, opts='_opts'):
        attr = '{}.{}'.format(opts, name)
        if default is not None:
            if callable(default):
                return rgetattr(self, attr, default())
            return rgetattr(self, attr, default)
        return rgetattr(self, attr)
        
    def _set_hash(self):
        if self._get_opt('make_hashable', False):
            def hashf(self):
                return hash(self._hashable())
            setattr(self, '__hash__', hashf)

    def _populate_data(self):
        self._data = Data()
        opt = Meta._get_opt
        # Generate attr display order
        self._data.attr_display_order = sorted(self._attrs.keys())
        
        # Generate attr documentation order
        tmp = []
        attrs = list(self._data.attr_display_order)
        for attr in opt(self, 'args', default=()):
            tmp.append(attr)
            attrs.remove(attr)
        tmp += attrs
        self._data.kw_attrs = attrs
        self._data.attr_documentation_order = tmp

        # Process metaclass_lookup
        sopt = partial(opt, opts='_seq_opts', default=list)
        for attr in sopt(self, 'metaclass_lookup'):
            attrs = sopt(self, attr)
            values = [getattr(self, attr_) for attr_ in attrs]
            values = type(attrs)(values)
            setattr(self._data, attr, values)

        # Register subclasses
        reg = partial(opt, name='register_subclasses', default=False)
        if reg(self):
            for c in self.mro():
                if hasmethod(c, '_get_opt'):
                    if reg(c):
                        if issubclass(self, c):
                            lst = rgetattr(c, '_data.subclasses')
                            if self not in lst:
                                lst.append(self)
                            c._data.subclasses = lst

    def _process_create_hooks(self):
        funcs = callables(self)
        hooks = [f for f in funcs.values() 
                 if getattr(f, 'is_create_hook', None) is _CreateHook]
        self._data.create_hooks = list(self._data.create_hooks) + hooks

        for hook in self._data.create_hooks:
            hook()

    def _combine_groups(self):
        if not hasattr(self, '_groups'):
            self._groups = GroupDict()
            return
        
        groups = self._groups
        if not isinstance(groups, GroupDict):
            for name in groups:
                if name not in self._attrs.groups:
                    self._attrs.groups[name] = set()

        groups = self._attrs.groups
        for base in self._class_data.bases:
            if hasattr(base, '_groups'):
                groups = combine(base._groups, groups)
        self._groups = groups
        self._groups['_all'] = self._attrs.attrs
        self._groups['_internal'] = self._attrs.internal

    def groups_enum(self):
        '''Returns an enum-ish dict with the names of the groups defined for this class.
        '''
        return ReflexiveDict(*self._groups.keys())


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Attr', 'Attrs', 'Meta', 'Data', 'create_hook', 'This')

#-------------------------------------------------------------------------------
