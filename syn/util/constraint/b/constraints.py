from .base import Constraint, Attr
from syn.type import Callable
from syn.five import STR

#-------------------------------------------------------------------------------
# Function


class FunctionConstraint(Constraint):
    _attrs = dict(func = Attr(Callable))
    _opts = dict(args = ('func', 'args'))

    def check(self, **kwargs):
        args = [kwargs[arg] for arg in self.args]
        return bool(self.func(*args))


#-------------------------------------------------------------------------------
# AllDifferent


class AllDifferentConstraint(Constraint):
    def check(self, **kwargs):
        vals = [kwargs[arg] for arg in self.args]
        return len(set(vals)) == len(self.args)


#-------------------------------------------------------------------------------
# EqualConstraint


class EqualConstraint(Constraint):
    _attrs = dict(arg = Attr(STR),
                  value = Attr(None))
    _opts = dict(args = ('arg', 'value'))

    def check(self, **kwargs):
        value = kwargs[self.arg]
        return value == self.value

    def preprocess(self, domain, **kwargs):
        domain[self.arg] = [self.value]


#-------------------------------------------------------------------------------
# __all__

__all__ = ('FunctionConstraint', 'AllDifferentConstraint', 'EqualConstraint')

#-------------------------------------------------------------------------------
