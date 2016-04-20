import six
from collections import defaultdict
import syn.base.a.meta as meta
from syn.base.a import Base
from syn.type.a import Type
from syn.type.a.ext import Callable, Sequence
from syn.base_utils import GroupDict, AttrDict
from functools import partial

STR = six.string_types

_Attr = meta.Attr
_OAttr = partial(_Attr, optional=True)

#-------------------------------------------------------------------------------
# Utilities

def group_combine(A, B):
    ret = type(A)(A)
    ret.combine(B)
    return ret

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
    )

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


class Attrs(meta.Attrs):
    def _update(self):
        super(Attrs, self)._update()
        self.call = {attr: spec.call for attr, spec in self.items() 
                     if spec.call}

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


class Meta(meta.Meta):
    _metaclass_data = AttrDict(attrs_type = Attrs)

    def __init__(self, clsname, bases, dct):
        super(Meta, self).__init__(clsname, bases, dct)
        self._combine_groups()

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
                vals = base._groups
                groups = group_combine(vals, groups)
        self._groups = groups


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Attr', 'Attrs', 'Meta')

#-------------------------------------------------------------------------------
