from .base import Constraint, Attr
from syn.type import Callable

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


class AllDifferent(Constraint):
    def check(self, **kwargs):
        vals = [kwargs[arg] for arg in self.args]
        return len(set(vals)) == len(self.args)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('FunctionConstraint', 'AllDifferent')

#-------------------------------------------------------------------------------
