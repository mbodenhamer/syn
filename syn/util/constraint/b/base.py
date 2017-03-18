from operator import itemgetter
from collections import MutableMapping, Sequence, defaultdict
from syn.base import Base, Attr, init_hook
from syn.type import Mapping, List
from syn.sets import SetNode, SetWrapper, TypeWrapper

#-------------------------------------------------------------------------------
# Domain


class Domain(Base):
    _attrs = dict(vars = Attr(Mapping(SetNode),
                              init=lambda self: dict()))
    _opts = dict(args = ('vars',))

    def __init__(self, *args, **kwargs):
        if not args and kwargs and not 'vars' in kwargs:
            kwargs = dict(vars = kwargs)
        if 'vars' in kwargs:
            for key in kwargs['vars']:
                value = kwargs['vars'][key]
                if not isinstance(value, SetNode):
                    if isinstance(value, type):
                        kwargs['vars'][key] = TypeWrapper(value)
                    else:
                        kwargs['vars'][key] = SetWrapper(value)
        super(Domain, self).__init__(*args, **kwargs)

    def __delitem__(self, key):
        del self.vars[key]

    def __getitem__(self, key):
        return self.vars[key]

    def __iter__(self):
        return iter(self.vars)

    def __len__(self):
        return len(self.vars)

    def __setitem__(self, key, value):
        if not isinstance(value, SetNode):
            if isinstance(value, type):
                self.vars[key] = TypeWrapper(value)
            else:
                self.vars[key] = SetWrapper(value)

    def copy(self, *args, **kwargs):
        return type(self)(self.vars.copy(*args, **kwargs))

    def display(self, **kwargs):
        ret = 'Domain('
        strs = ['{} = {}'.format(var, vals.display(**kwargs))
                for var, vals in sorted(self.vars.items(), key=itemgetter(0))]
        ret += ',\n       '.join(strs) + ')'
        return ret


MutableMapping.register(Domain)

#-------------------------------------------------------------------------------
# Constraint


class Constraint(Base):
    _attrs = dict(args = Attr(Sequence,
                              init=lambda self: tuple()))
    _opts = dict(init_validate = True,
                 args = ('args',),
                 make_hashable = True)

    def check(self, **kwargs):
        raise NotImplementedError

    def display(self, **kwargs):
        pass

    def preprocess(self, domain, **kwargs):
        pass
    

#-------------------------------------------------------------------------------
# Problem


class Problem(Base):
    _attrs = dict(constraints = Attr(List(Constraint)),
                  domain = Attr(Domain))
    _opts = dict(init_validate = True,
                 args = ('domain', 'constraints'))

    @init_hook
    def _init(self):
        self.domain = self.domain.copy()
        self.var_constraint = defaultdict(set)
        
        for con in self.constraints:
            con.preprocess(self.domain)
            for var in con.args:
                self.var_constraint[var].add(con)

    def check(self, theory):
        for con in self.constraints:
            if set(con.args) <= set(theory):
                if not con.check(**theory):
                    return False
        return True

    def display(self, **kwargs):
        strs = [self.domain.display(**kwargs)]
        for con in self.constraints:
            s = con.display(**kwargs)
            if s:
                strs.append(s)
        return '\n'.join(strs)

    def validate(self):
        super(Problem, self).validate()

        if not set(self.var_constraint).issubset(set(self.domain)):
            raise ValueError('Some constraints defined in over '
                             'undefined variables')
            

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Domain', 'Constraint', 'Problem')

#-------------------------------------------------------------------------------
