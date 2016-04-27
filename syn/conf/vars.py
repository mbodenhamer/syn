import os
import collections
from functools import partial
from jinja2 import Template
from syn.base_utils import (AttrDict, SeqDict, dictify_strings, AssocDict,
                            GroupDict, compose)
from syn.base import Base, Attrs, Attr
from syn.type import Mapping, Dict
from syn.five import STR

dictify = partial(dictify_strings, sep='=', typ=AssocDict)
ADict = partial(Mapping, map_type=AssocDict)

#-------------------------------------------------------------------------------
# Utilities

def add_eq(lst):
    if isinstance(lst, collections.Sequence):
        ret = []
        for val in lst:
            if '=' not in val:
                val += '='
            ret.append(val)
        return ret
    return lst
        
#-------------------------------------------------------------------------------
# Vars Context


class VarsContext(Base):
    pass


#-------------------------------------------------------------------------------
# Vars Mixin


class VarsMixin(object):
    _attrs = Attrs(vars = Attr(ADict(STR), call=compose(dictify, add_eq),
                               default={}, doc='A dictionary of variables'),
                   _env = Attr(Dict(None), doc='Variable environment',
                               internal=True),
                  )
    _opts = AttrDict(env_default = False)
    _groups = GroupDict(vars = set(['vars']),
                        internal = set(['_env']))

    def _populate_environment(self):
        env = {}
        if self._opts.env_default:
            env.update(os.environ)
        env.update(self.to_dict('vars', 'internal'))

        for var, val in list(self.vars.items()):
            if not isinstance(val, STR):
                env[var] = val

            template = Template(val)
            env[var] = template.render(env)

        self._env = env

    _seq_opts = SeqDict(init_hooks = (_populate_environment,))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('VarsMixin',)

#-------------------------------------------------------------------------------
