from .base import PythonNode, Context, Attr, AST, ACO, Load
from syn.five import STR

#-------------------------------------------------------------------------------
# Name


class Name(PythonNode):
    _attrs = dict(ctx = Attr(Context, Load(), groups=(AST, ACO)),
                  id = Attr(STR, group=AST))
    _opts = dict(max_len = 0,
                 args = ('id',))

    def emit(self, **kwargs):
        ret = ' ' * kwargs.get('col_offset', self.col_offset)
        ret += self.id
        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        ret = cls(**kwargs)
        return ret

    def to_ast(self, **kwargs):
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(**kwargs_)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Name',)

#-------------------------------------------------------------------------------
