from .base import PythonNode, Attr, Context, Load, AST, ACO
from syn.base_utils import quote_string, setitem
from syn.type.a import List
from syn.five import PY2, STR

#-------------------------------------------------------------------------------
# Base Class


class Literal(PythonNode):
    _opts = dict(max_len = 0)


#-------------------------------------------------------------------------------
# Num

if PY2:
    n_type = (int, long, float, complex)
else:
    n_type = (int, float, complex)


class Num(Literal):
    _opts = dict(args = ('n',))
    _attrs = dict(n = Attr(n_type, doc='The numerical value', group=AST))

    def emit(self, **kwargs):
        ret = self._indent(**kwargs)
        ret += str(self.n)
        return ret
    

#-------------------------------------------------------------------------------
# Str


class Str(Literal):
    _opts = dict(args = ('s',))
    _attrs = dict(s = Attr(STR, doc='The string contents', group=AST))

    def emit(self, **kwargs):
        ret = self._indent(**kwargs)
        ret += quote_string(self.s)
        return ret


#-------------------------------------------------------------------------------
# Bytes


class Bytes(Literal):
    minver = '3'
    _attrs = dict(s = Attr(bytes, group=AST))

    def emit(self, **kwargs):
        ret = self._indent(**kwargs)
        ret += str(self.s)
        return ret


#-------------------------------------------------------------------------------
# Sequence


class Sequence(Literal):
    bounds = ('[', ']')
    delim = ', '
    _attrs = dict(elts = Attr(List(PythonNode), groups=(AST, ACO)))
    
    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            cs = [c.emit(**kwargs) for c in self.elts]
        ret = self.delim.join(cs)
        if len(cs) == 1 and isinstance(self, Tuple):
            ret += ','
        ret = self.bounds[0] + ret + self.bounds[1]
        ret = self._indent(**kwargs) + ret
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

__all__ = ('Literal', 'Num', 'Str', 'Bytes',
           'Sequence', 'List', 'Tuple', 'Set')

#-------------------------------------------------------------------------------
