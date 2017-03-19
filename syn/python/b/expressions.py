from operator import itemgetter
from syn.base_utils import setitem
from .base import PythonNode, from_ast, Attr, AST, ACO, col_offset

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
# BinaryOperator


class BinaryOperator(PythonNode):
    symbol = None

    def emit(self, **kwargs):
        return self.symbol

    @classmethod
    def from_ast(cls, ast, **kwargs):
        return cls(**kwargs)

    def to_ast(self, **kwargs):
        return self.ast()


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
    _opts = dict(max_len = 2,
                 min_len = 2,
                 args = ('op',))
    _attrs = dict(op = Attr(BinaryOperator, groups=(AST, ACO)))

    A = property(itemgetter(0))
    B = property(itemgetter(1))

    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            A = self.A.emit(**kwargs)
            B = self.B.emit(**kwargs)
            op = self.op.emit(**kwargs)

        ret = ' ' * col_offset(self, kwargs)
        ret += '({} {} {})'.format(A, op, B)
        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        A = from_ast(ast.left, **kwargs)
        B = from_ast(ast.right, **kwargs)
        op = from_ast(ast.op, **kwargs)
        ret = cls(A, B, op=op)
        return ret

    def to_ast(self, **kwargs):
        A = self.A.to_ast(**kwargs)
        B = self.B.to_ast(**kwargs)
        op = self.op.to_ast(**kwargs)
        return self.ast(A, op, B)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Expr',
           'BinaryOperator', 'BinOp',
           'Add', 'Sub', 'Mult', 'Div')

#-------------------------------------------------------------------------------

