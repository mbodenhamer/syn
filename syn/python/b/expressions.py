from operator import attrgetter
from syn.base_utils import setitem
from .base import PythonNode, Attr, AST, ACO, col_offset

#-------------------------------------------------------------------------------
# Expr


class Expr(PythonNode):
    _attrs = dict(value = Attr(PythonNode, groups=(AST, ACO)))
    _opts = dict(max_len = 0,
                 args = ('value',))

    def emit(self, **kwargs):
        return self.value.emit(**kwargs)


#-------------------------------------------------------------------------------
# BinaryOperator


class BinaryOperator(PythonNode):
    symbol = None

    def emit(self, **kwargs):
        return self.symbol


#-------------------------------------------------------------------------------
# Binary Operators


class Add(BinaryOperator):
    symbol = '+'

class Sub(BinaryOperator):
    symbol = '-'

class Mult(BinaryOperator):
    symbol = '*'

class Div(BinaryOperator):
    symbol = '/'


#-------------------------------------------------------------------------------
# BinOp


class BinOp(PythonNode):
    _opts = dict(max_len = 0,
                 args = ('left', 'op', 'right'))
    _attrs = dict(op = Attr(BinaryOperator, groups=(AST, ACO)),
                  left = Attr(PythonNode, groups=(AST, ACO)),
                  right = Attr(PythonNode, groups=(AST, ACO)))

    A = property(attrgetter('left'))
    B = property(attrgetter('right'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            A = self.A.emit(**kwargs)
            B = self.B.emit(**kwargs)
            op = self.op.emit(**kwargs)

        ret = ' ' * col_offset(self, kwargs)
        ret += '({} {} {})'.format(A, op, B)
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Expr',
           'BinaryOperator', 'BinOp',
           'Add', 'Sub', 'Mult', 'Div')

#-------------------------------------------------------------------------------

