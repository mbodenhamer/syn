from operator import attrgetter
from syn.base_utils import setitem
from .base import PythonNode, Attr, AST, ACO, Context, Load
from syn.type.a import List
from syn.five import STR

#-------------------------------------------------------------------------------
# Expression


class Expression_(PythonNode):
    _opts = dict(max_len = 0)


#-------------------------------------------------------------------------------
# Expr


class Expr(Expression_):
    _attrs = dict(value = Attr(PythonNode, groups=(AST, ACO)))
    _opts = dict(args = ('value',))

    def emit(self, **kwargs):
        return self.value.emit(**kwargs)


#-------------------------------------------------------------------------------
# BinaryOperator


class BinaryOperator(Expression_):
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


class BinOp(Expression_):
    _opts = dict(args = ('left', 'op', 'right'))
    _attrs = dict(op = Attr(BinaryOperator, groups=(AST, ACO)),
                  left = Attr(PythonNode, groups=(AST, ACO)),
                  right = Attr(PythonNode, groups=(AST, ACO)))

    A = property(attrgetter('left'))
    B = property(attrgetter('right'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            A = self.A.emit(**kwargs)
            B = self.B.emit(**kwargs)
            op = self.op.emit(**kwargs)

        ret = self._indent(**kwargs)
        ret += '({} {} {})'.format(A, op, B)
        return ret


#-------------------------------------------------------------------------------
# Comparator


class Comparator(BinaryOperator):
    pass

#-------------------------------------------------------------------------------
# Comparators


class Eq(Comparator):
    symbol = '=='

class NotEq(Comparator):
    symbol = '!='

class Lt(Comparator):
    symbol = '<'

class LtE(Comparator):
    symbol = '<='

class Gt(Comparator):
    symbol = '>'

class GtE(Comparator):
    symbol = '>='

class Is(Comparator):
    symbol = 'is'

class IsNot(Comparator):
    symbol = 'is not'

class In(Comparator):
    symbol = 'in'

class NotIn(Comparator):
    symbol = 'not in'


#-------------------------------------------------------------------------------
# Compare


class Compare(Expression_):
    _attrs = dict(left = Attr(PythonNode, groups=(AST, ACO)),
                  ops = Attr(List(Comparator), groups=(AST, ACO)),
                  comparators = Attr(List(PythonNode), groups=(AST, ACO)))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            left = self.left.emit(**kwargs)
            ops = [op.emit(**kwargs) for op in self.ops]
            comps = [comp.emit(**kwargs) for comp in self.comparators]

        ret = self._indent(**kwargs) + left
        for op, comp in zip(ops, comps):
            ret += ' {} {}'.format(op, comp)
        ret = '(' + ret + ')'
        return ret
            

#-------------------------------------------------------------------------------
# Attribute


class Attribute(Expression_):
    _attrs = dict(value = Attr(PythonNode, groups=(AST, ACO)),
                  attr = Attr(STR, group=AST),
                  ctx = Attr(Context, Load(), groups=(AST, ACO)))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            value = self.value.emit(**kwargs)
        
        ret = self._indent(**kwargs)
        ret += value + '.' + self.attr
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Expression_', 'Expr',
           'BinaryOperator', 'BinOp',
           'Add', 'Sub', 'Mult', 'Div',
           'Comparator', 'Compare',
           'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn',
           'Attribute',)

#-------------------------------------------------------------------------------

