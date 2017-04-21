from .base import Expression, Context, Attr, AST, ACO, Load
from syn.base_utils import setitem
from syn.five import STR

#-------------------------------------------------------------------------------
# Name


class Name(Expression):
    _attrs = dict(ctx = Attr(Context, Load(), groups=(AST, ACO)),
                  id = Attr(STR, group=AST))
    _opts = dict(max_len = 0,
                 args = ('id',))

    def emit(self, **kwargs):
        ret = self._indent(**kwargs)
        ret += self.id
        return ret

    def variables(self, **kwargs):
        return {self.id}


#-------------------------------------------------------------------------------
# Starred


class Starred(Expression):
    minver = '3'
    _attrs = dict(value = Attr(Name, groups=(AST, ACO)),
                  ctx = Attr(Context, Load(), groups=(AST, ACO)))
    _opts = dict(max_len = 0,
                 args = ('value',))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            value = self.value.emit(**kwargs)
            
        ret = self._indent(**kwargs)
        ret += '*' + value
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Name', 'Starred')

#-------------------------------------------------------------------------------
