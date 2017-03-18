from operator import itemgetter
from .base import PythonNode, from_ast

#-------------------------------------------------------------------------------
# Expr


class Expr(PythonNode):
    _opts = dict(min_len = 1,
                 max_len = 1)
    body = property(itemgetter(0))

    def emit(self, **kwargs):
        return self.body.emit(**kwargs)

    @classmethod
    def from_ast(cls, ast, **kwargs):
        child = from_ast(ast.value, **kwargs)
        ret = cls(child, **kwargs)
        return ret

    def to_ast(self, **kwargs):
        body = self.body.to_ast(**kwargs)
        return self.ast(body)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Expr',)

#-------------------------------------------------------------------------------

