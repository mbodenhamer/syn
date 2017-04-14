import ast
from .base import PythonNode, Attr, AST, ACO, OAttr, Statement
from syn.base_utils import setitem, get_typename
from syn.type.a import List
from syn.five import STR

#-------------------------------------------------------------------------------
# Assign


class Assign(Statement):
    _attrs = dict(targets = Attr(List(PythonNode), groups=(AST, ACO)),
                  value = Attr(PythonNode, groups=(AST, ACO)))
    _opts = dict(args = ('targets', 'value'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            targs = [targ.emit(**kwargs) for targ in self.targets]
            val = self.value.emit(**kwargs)

        ret = self._indent(**kwargs)
        ret += ' = '.join(targs)
        ret += ' = ' + val
        return ret


#-------------------------------------------------------------------------------
# Return


class Return(Statement):
    _attrs = dict(value = OAttr(PythonNode, groups=(AST, ACO)))
    _opts =  dict(args = ('value',))

    def emit(self, **kwargs):
        if self.value is not None:
            with setitem(kwargs, 'indent_level', 0):
                val = self.value.emit(**kwargs)

        ret = self._indent(**kwargs)
        ret += 'return'
        if self.value is not None:
            ret += ' ' + val
        return ret


#-------------------------------------------------------------------------------
# Import


class Alias(Statement):
    ast = ast.alias
    _attrs = dict(name = Attr(STR, group=AST),
                  asname = Attr(STR, optional=True, group=AST))
    _opts = dict(args = ('name', 'asname'))

    def emit(self, **kwargs):
        ret = self.name
        if self.asname:
            ret += ' as ' + self.asname
        return ret


class Import(Statement):
    _attrs = dict(names = Attr(List(Alias), groups=(AST, ACO)))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            strs = [val.emit(**kwargs) for val in self.names]
            names = ', '.join(strs)

        ret = self._indent(**kwargs)
        ret += 'import ' + names
        return ret


#-------------------------------------------------------------------------------
# Empty Statements


class EmptyStatement(Statement):
    def emit(self, **kwargs):
        ret = self._indent(**kwargs)
        ret += get_typename(self).lower()
        return ret


class Break(EmptyStatement):
    pass


class Continue(EmptyStatement):
    pass


class Pass(EmptyStatement):
    def as_return(self, **kwargs):
        return Return()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Assign', 'Return',
           'Alias', 'Import',
           'EmptyStatement', 'Break', 'Continue', 'Pass')

#-------------------------------------------------------------------------------
