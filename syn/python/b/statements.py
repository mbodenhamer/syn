from .base import PythonNode, Attr, AST, ACO, col_offset, from_ast
from syn.base_utils import setitem
from syn.type.a import List

#-------------------------------------------------------------------------------
# Statement


class Statement(PythonNode):
    _opts = dict(max_len = 0)


#-------------------------------------------------------------------------------
# Assign


class Assign(Statement):
    _attrs = dict(targets = Attr(List(PythonNode)),
                  value = Attr(PythonNode))
    _opts = dict(args = ('targets', 'value'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            targs = [targ.emit(**kwargs) for targ in self.targets]
            val = self.value.emit(**kwargs)

        ret = ' ' * col_offset(self, kwargs)
        ret += ' = '.join(targs)
        ret += ' = ' + val
        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        targs = [from_ast(targ, **kwargs) for targ in ast.targets]
        val = from_ast(ast.value, **kwargs)
        return cls(targs, val)

    def to_ast(self, **kwargs):
        targs = [targ.to_ast(**kwargs) for targ in self.targets]
        val = self.value.to_ast(**kwargs)
        return self.ast(targs, val)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Statement',
           'Assign')

#-------------------------------------------------------------------------------
