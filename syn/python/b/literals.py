from .base import PythonNode, Attr, Context, Load, AST, ACO, \
    col_offset
from syn.base_utils import quote_string, setitem
from syn.type.a import List
from syn.five import PY2, STR

#-------------------------------------------------------------------------------
# Base Class


class Literal(PythonNode):
    pass


#-------------------------------------------------------------------------------
# Num

if PY2:
    n_type = (int, long, float, complex)
else:
    n_type = (int, float, complex)


class Num(Literal):
    _opts = dict(max_len = 0,
                 args = ('n',))
    _attrs = dict(n = Attr(n_type, doc='The numerical value', group=AST))

    def emit(self, **kwargs):
        ret = ' ' * col_offset(self, kwargs)
        ret += str(self.n)
        return ret
    

#-------------------------------------------------------------------------------
# Str


class Str(Literal):
    _opts = dict(max_len = 0,
                 args = ('s',))
    _attrs = dict(s = Attr(STR, doc='The string contents', group=AST))

    def emit(self, **kwargs):
        ret = ' ' * col_offset(self, kwargs)
        ret += quote_string(self.s)
        return ret


#-------------------------------------------------------------------------------
# Sequence


class Sequence(Literal):
    bounds = ('[', ']')
    delim = ', '
    _attrs = dict(elts = Attr(List(PythonNode), groups=(AST, ACO)))
    
    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            cs = [c.emit(**kwargs) for c in self.elts]
        ret = self.delim.join(cs)
        if len(cs) == 1 and isinstance(self, Tuple):
            ret += ','
        ret = self.bounds[0] + ret + self.bounds[1]
        ret = ' ' * col_offset(self, kwargs) + ret
        return ret


#-------------------------------------------------------------------------------
# List


class List(Sequence):
    _attrs = dict(ctx = Attr(Context, Load(), groups=(AST, ACO)))


#-------------------------------------------------------------------------------
# Tuple


class Tuple(List):
    bounds = ('(', ')')


#-------------------------------------------------------------------------------
# Set


class Set(Sequence):
    bounds = ('{', '}')


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Literal', 'Num', 'Str',
           'Sequence', 'List', 'Tuple', 'Set')

#-------------------------------------------------------------------------------
