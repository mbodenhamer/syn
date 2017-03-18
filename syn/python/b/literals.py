from .base import PythonNode, Attr
from syn.base_utils import quote_string
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
    _attrs = dict(n = Attr(n_type, doc='The numerical value'))

    @classmethod
    def from_ast(cls, ast, **kwargs):
        ret = cls(n = ast.n, **kwargs)
        return ret

    def emit(self, **kwargs):
        ret = ' ' * kwargs.get('col_offset', self.col_offset)
        ret += str(self.n)
        return ret
    
    def to_ast(self, **kwargs):
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(self.n, **kwargs_)


#-------------------------------------------------------------------------------
# Str


class Str(Literal):
    _opts = dict(max_len = 0,
                 args = ('s',))
    _attrs = dict(s = Attr(STR, doc='The string contents'))

    @classmethod
    def from_ast(cls, ast, **kwargs):
        ret = cls(s = ast.s, **kwargs)
        return ret

    def emit(self, **kwargs):
        ret = ' ' * kwargs.get('col_offset', self.col_offset)
        ret += quote_string(self.s)
        return ret

    def to_ast(self, **kwargs):
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(self.s, **kwargs_)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Literal', 'Num')

#-------------------------------------------------------------------------------
