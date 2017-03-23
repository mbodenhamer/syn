from .base import PythonNode, Context, Attr, AST, ACO, Load, col_offset
from syn.five import STR

#-------------------------------------------------------------------------------
# Name


class Name(PythonNode):
    _attrs = dict(ctx = Attr(Context, Load(), groups=(AST, ACO)),
                  id = Attr(STR, group=AST))
    _opts = dict(max_len = 0,
                 args = ('id',))

    def emit(self, **kwargs):
        ret = ' ' * col_offset(self, kwargs)
        ret += self.id
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Name',)

#-------------------------------------------------------------------------------
