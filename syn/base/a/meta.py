from copy import deepcopy
from syn.type.a import Type, This
from syn.base_utils import UpdateDict, AttrDict, SeqDict, mro, rgetattr

#-------------------------------------------------------------------------------
# Utilities

def combine(A, B):
    ret = deepcopy(A)
    ret.update(B)
    return ret

def graft(coll, branch, index):
    '''Graft list branch into coll at index
    '''
    pre = coll[:index]
    post = coll[index:]
    ret = pre + branch + post
    return ret

def metaclasses(bases):
    ''' Returns 'proper' metaclasses for the classes in bases
    '''
    ret = []
    metas = [type(base) for base in bases]
    for k,meta in enumerate(metas):
        if not any(issubclass(m, meta) for m in metas[k+1:]):
            ret.append(meta)

    if type in ret:
        ret.remove(type)
    return ret

def _bases(cls):
    ret = mro(cls)
    if ret[-1] is object or ret[-1] is type:
        ret.pop()  # remove object (or type)
    return ret

def sorted_bases(bases):
    '''If a class subclasses each class in bases (in that order), then
    this function returns the would-be python mro for the created class,
    minus <object>.
    '''
    ret = []

    for base in bases:
        # lst = [super(base), super(super(base)), ..., highest_base]
        lst = _bases(base)

        if not ret:
            ret = lst
        elif not any(b in ret for b in lst):
            ret += lst
        else:
            buf = []
            for b in lst:
                if b in ret:
                    if buf:
                        ret = graft(ret, buf, ret.index(b))
                        buf = []
                else:
                    buf.append(b)
            if buf:
                ret += buf

    return ret

#-------------------------------------------------------------------------------
# Alias Property

def alias_property(attr):
    def getter(self):
        return getattr(self, attr)
    def setter(self, value):
        return setattr(self, attr, value)
    def deller(self):
        return delattr(self, attr)
    ret = property(getter, setter, deller)
    return ret

#-------------------------------------------------------------------------------
# Object Attribute


class Attr(object):
    def __init__(self, typ=None, default=None, doc='', optional=False, init=None):
        self.type = Type.dispatch(typ)
        self.default = default
        self.doc = doc
        self.optional = optional
        self.init = init


#-------------------------------------------------------------------------------
# Object Attrs Bookkeeping


class Attrs(UpdateDict):
    def _update(self):
        self.attrs = set(self.keys())
        self.types = {attr: spec.type for attr, spec in self.items()}
        self.required = {attr for attr, spec in self.items() 
                         if not spec.optional}
        self.optional = {attr for attr, spec in self.items() if spec.optional}
        self.defaults = {attr: spec.default for attr, spec in self.items()
                         if spec.default is not None}
        self.doc = {attr: spec.doc for attr, spec in self.items() if spec.doc}
        self.init = {attr: spec.init for attr, spec in self.items()
                     if spec.init is not None}


#-------------------------------------------------------------------------------
# Metaclass


class Meta(type):
    _metaclass_opts = AttrDict(attrs_type = Attrs,
                               aliases_type = SeqDict,
                               opts_type = AttrDict,
                               seq_opts_type = SeqDict)

    def __init__(self, clsname, bases, dct):
        super(Meta, self).__init__(clsname, bases, dct)

        self._class_data = AttrDict()        
        self._class_data.bases = tuple(sorted_bases(bases))
        self._class_data.def_bases = bases
        self._class_data.clsname = clsname
        self._class_data.dct = dict(dct)

        self._resolve_this()
        self._combine_attr_fast_update('_attrs', 
                                       self._metaclass_opts.attrs_type)
        self._combine_attr('_opts', self._metaclass_opts.opts_type)
        self._combine_attr_dct('_seq_opts', self._metaclass_opts.seq_opts_type)
        self._combine_attr_dct('_aliases', self._metaclass_opts.aliases_type)

        self._resolve_aliases()

    def _resolve_this(self):
        attrs = getattr(self, '_attrs', {}).values()
        for attr in attrs:
            if isinstance(attr.type, This):
                attr.type = Type.dispatch(self)

    def _combine_attr(self, attr, typ=None):
        values = getattr(self, attr, {})
        if typ is not None:
            values = typ(values)
        
        for base in self._class_data.bases:
            vals = getattr(base, attr, {})
            if typ is not None:
                vals = typ(vals)
            values = combine(vals, values)

        setattr(self, attr, values)

    def _combine_attr_dct(self, attr, typ=None):
        values = self._class_data.dct.get(attr, {})
        if typ is not None:
            values = typ(values)
        
        for base in self._class_data.bases:
            vals = rgetattr(base, '_class_data.dct', {}).get(attr, {})
            if typ is not None:
                vals = typ(vals)
            values = combine(vals, values)

        setattr(self, attr, values)

    def _combine_attr_fast_update(self, attr, typ):
        '''Avoids having to call _update for each intermediate base.  Only
        works for class attr of type UpdateDict.

        '''
        values = dict(getattr(self, attr, {}))
        
        for base in self._class_data.bases:
            vals = dict(getattr(base, attr, {}))
            values = combine(vals, values)
            
        setattr(self, attr, typ(values))

    def _resolve_aliases(self):
        for attr, aliases in self._aliases.items():
            for alias in aliases:
                if not isinstance(getattr(self, alias, None), property):
                    setattr(self, alias, alias_property(attr))



#-------------------------------------------------------------------------------
# __all__

__all__ = ('Attr', 'Attrs', 'Meta',)

#-------------------------------------------------------------------------------
