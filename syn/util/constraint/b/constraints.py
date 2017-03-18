from .base import Constraint, Attr
from syn.base import init_hook
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

    def display(self, **kwargs):
        return 'Function({}, {})'.format(self.func, 
                                         ', '.join(map(str, self.args)))


#-------------------------------------------------------------------------------
# AllDifferent


class AllDifferentConstraint(Constraint):
    def check(self, **kwargs):
        vals = [kwargs[arg] for arg in self.args]
        return len(set(vals)) == len(self.args)

    def display(self, **kwargs):
        return 'AllDifferent({})'.format(', '.join(map(str, self.args)))


#-------------------------------------------------------------------------------
# EqualConstraint


class EqualConstraint(Constraint):
    _attrs = dict(arg = Attr(STR),
                  value = Attr(None))
    _opts = dict(args = ('arg', 'value'))

    @init_hook
    def _set_args(self):
        self.args = [self.arg]

    def check(self, **kwargs):
        value = kwargs[self.arg]
        return value == self.value

    def display(self, **kwargs):
        return '{} == {}'.format(self.arg, self.value)

    def preprocess(self, domain, **kwargs):
        domain[self.arg] = [self.value]


#-------------------------------------------------------------------------------
# __all__

__all__ = ('FunctionConstraint', 'AllDifferentConstraint', 'EqualConstraint')

#-------------------------------------------------------------------------------
