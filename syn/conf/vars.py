import os
import collections
from functools import partial
from jinja2 import Template
from syn.base_utils import AttrDict, dictify_strings, AssocDict
from syn.base import Base

dictify = partial(dictify_strings, sep='=', typ=AssocDict)

#-------------------------------------------------------------------------------
# Utilities

def add_eq(lst):
    ret = []
    for val in lst:
        if '=' not in val:
            val += '='
        ret.append(val)
    return ret
        
#-------------------------------------------------------------------------------
# Vars


class Vars(Base):
    _opts = AttrDict(env_default = False)

    @classmethod
    def coerce(cls, value):
        if not isinstance(value, collections.Mapping):
            value = dictify(add_eq(value))

        env = {}
        if cls._opts.env_default:
            env.update(os.environ)

        types = cls._attrs.types
        for var, val in list(value.items()):
            template = Template(val)
            newval = template.render(env)
            env[var] = types[var].coerce(newval)
            value[var] = newval
            
        return super(Vars, cls).coerce(value)


#-------------------------------------------------------------------------------
# Vars Mixin


# class VarsMixin(object):
#     _attrs = Attrs(vars = Attr(Vars, optional=True))
#     _opts = AttrDict(env_default = False)

#     def _resolve_vars(cls, dct):
#         types = cls._attrs.types
#         if 'vars' in dct:
#             dct['vars'] = types['vars'].coerce(dct['vars'])

#         env = {}
#         if cls._opts.env_default:
#             env.update(os.environ)
#         env.update(dct['vars'].to_dict())

#         for var, val in list(dct.items()):
#             if var == 'vars':
#                 continue

#             if isinstance(val, STR):
#                 template = Template(val)
#                 dct[var] = template.render(env)

#     _seq_opts = SeqDict(coerce_hooks = (_resolve_vars,))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Vars',)

#-------------------------------------------------------------------------------
