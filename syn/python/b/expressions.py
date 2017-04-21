import ast
from functools import partial
from operator import attrgetter
from syn.base_utils import setitem, pyversion
from .base import PythonNode, Attr, AST, ACO, Context, Load, Expression, CC
from syn.type.a import List
from syn.five import STR

VER = pyversion()
OAttr = partial(Attr, optional=True)

#-------------------------------------------------------------------------------
# Expr


class Expr(Expression):
    _attrs = dict(value = Attr(PythonNode, groups=(AST, ACO)))
    _opts = dict(args = ('value',))

    def emit(self, **kwargs):
        return self.value.emit(**kwargs)


#-------------------------------------------------------------------------------
# Operator


class Operator(Expression):
    symbol = None

    def emit(self, **kwargs):
        return self.symbol


#-------------------------------------------------------------------------------
# UnaryOperator


class UnaryOperator(Operator):
    pass


#-------------------------------------------------------------------------------
# Unary Operators


class UAdd(UnaryOperator):
    symbol = '+'

class USub(UnaryOperator):
    symbol = '-'

class Not(UnaryOperator):
    symbol = 'not'

class Invert(UnaryOperator):
    symbol = '~'


#-------------------------------------------------------------------------------
# UnaryOp


class UnaryOp(Expression):
    _opts = dict(args = ['op', 'operand'])
    _attrs = dict(op = Attr(UnaryOperator, groups=(AST, ACO)),
                  operand = Attr(Expression, groups=(AST, ACO)))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            op = self.op.emit(**kwargs)
            operand = self.operand.emit(**kwargs)

        ret = self._indent(**kwargs)
        if isinstance(self.op, Not):
            ret += '({} {})'.format(op, operand)
        else:
            ret += '{}{}'.format(op, operand)
        return ret


#-------------------------------------------------------------------------------
# BinaryOperator


class BinaryOperator(Operator):
    pass


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

class FloorDiv(BinaryOperator):
    symbol = '//'

class Mod(BinaryOperator):
    symbol = '%'

class Pow(BinaryOperator):
    symbol = '**'

class LShift(BinaryOperator):
    symbol = '<<'

class RShift(BinaryOperator):
    symbol = '>>'

class BitOr(BinaryOperator):
    symbol = '|'

class BitXor(BinaryOperator):
    symbol = '^'

class BitAnd(BinaryOperator):
    symbol = '&'

class MatMult(BinaryOperator):
    minver = '3.5'
    symbol = '@'
    

#-------------------------------------------------------------------------------
# BinOp


class BinOp(Expression):
    _opts = dict(args = ('left', 'op', 'right'))
    _attrs = dict(op = Attr(BinaryOperator, groups=(AST, ACO)),
                  left = Attr(Expression, groups=(AST, ACO)),
                  right = Attr(Expression, groups=(AST, ACO)))

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
# BooleanOperator


class BooleanOperator(Operator):
    pass


#-------------------------------------------------------------------------------
# Boolean Operators


class And(BooleanOperator):
    symbol = 'and'

class Or(BooleanOperator):
    symbol = 'or'


#-------------------------------------------------------------------------------
# BoolOp


class BoolOp(Expression):
    _opts = dict(args = ('op', 'values'))
    _attrs = dict(op = Attr(BooleanOperator, groups=(AST, ACO)),
                  values = Attr(List(Expression), groups=(AST, ACO, CC)))
    
    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            op = ' ' + self.op.emit(**kwargs) + ' '
            vals = [val.emit(**kwargs) for val in self.values]

        ret = op.join(vals)
        ret = '(' + ret + ')'
        ret = self._indent(**kwargs) + ret
        return ret
        

#-------------------------------------------------------------------------------
# Comparator


class Comparator(Operator):
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


class Compare(Expression):
    _opts = dict(args = ('left', 'ops', 'comparators'))
    _attrs = dict(left = Attr(Expression, groups=(AST, ACO)),
                  ops = Attr(List(Comparator), groups=(AST, ACO, CC)),
                  comparators = Attr(List(Expression), groups=(AST, ACO, CC)))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            left = self.left.emit(**kwargs)
            ops = [op.emit(**kwargs) for op in self.ops]
            comps = [comp.emit(**kwargs) for comp in self.comparators]

        ret = left
        for op, comp in zip(ops, comps):
            ret += ' {} {}'.format(op, comp)
        ret = '(' + ret + ')'
        ret = self._indent(**kwargs) + ret
        return ret
            

#-------------------------------------------------------------------------------
# keyword


class Keyword(Expression):
    ast = ast.keyword
    _attrs = dict(arg = Attr(STR, group=AST),
                  value = Attr(Expression, groups=(AST, ACO)))
    _opts = dict(args = ('arg', 'value'))
    
    if VER >= '3.5':
        _attrs['arg'] = Attr((STR, type(None)), group=AST)

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            value = self.value.emit(**kwargs)

        if self.arg is None:
            ret = '**' + value
        else:
            ret = '{}={}'.format(self.arg, value)
        return ret


#-------------------------------------------------------------------------------
# Call


class Call(Expression):
    _opts = dict(args = ['func', 'args', 'keywords'])
    _attrs = dict(func = Attr(Expression, groups=(AST, ACO)),
                  args = OAttr(List(Expression), groups=(AST, ACO, CC)),
                  keywords = OAttr(List(Keyword), groups=(AST, ACO, CC)))
    
    if VER < '3.5':
        _attrs['starargs'] = OAttr(PythonNode, groups=(AST, ACO))
        _attrs['kwargs'] = OAttr(PythonNode, groups=(AST, ACO))
        _opts['args'].extend(['starargs', 'kwargs'])

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            func = self.func.emit(**kwargs)
            args = [arg.emit(**kwargs) for arg in self.args] if self.args else []
            kwds = [kw.emit(**kwargs) for kw in self.keywords] if self.keywords else []

            if VER < '3.5':
                starargs = self.starargs.emit(**kwargs) if self.starargs else ''
                kwargs_ = self.kwargs.emit(**kwargs) if self.kwargs else ''
            else:
                starargs = ''
                kwargs_ = ''

        strs = []
        ret = self._indent(**kwargs) + func + '('
        if args:
            strs.extend(args)
        if kwds:
            strs.extend(kwds)
        if starargs:
            strs.append('*' + starargs)
        if kwargs_:
            strs.append('**' + kwargs_)
        ret += ', '.join(strs)
        ret += ')'
        return ret


#-------------------------------------------------------------------------------
# IfExp


class IfExp(Expression):
    _attrs = dict(test = Attr(Expression, groups=(AST, ACO)),
                  body = Attr(Expression, groups=(AST, ACO)),
                  orelse = Attr(Expression, groups=(AST, ACO)))
    _opts = dict(args = ('test', 'body', 'orelse'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            test = self.test.emit(**kwargs)
            body = self.body.emit(**kwargs)
            orelse = self.orelse.emit(**kwargs)

        ret = self._indent(**kwargs)
        ret += '({} if {} else {})'.format(body, test, orelse)
        return ret


#-------------------------------------------------------------------------------
# Attribute


class Attribute(Expression):
    _attrs = dict(value = Attr(Expression, groups=(AST, ACO)),
                  attr = Attr(STR, group=AST),
                  ctx = Attr(Context, Load(), groups=(AST, ACO)))
    _opts = dict(args = ('value', 'attr'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            value = self.value.emit(**kwargs)
        
        ret = self._indent(**kwargs)
        ret += value + '.' + self.attr
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Expr',
           'Operator', 'UnaryOperator', 'UnaryOp',
           'UAdd', 'USub', 'Not', 'Invert',
           'BinaryOperator', 'BinOp',
           'Add', 'Sub', 'Mult', 'Div', 'FloorDiv', 'Mod', 'Pow', 'LShift',
           'RShift', 'BitOr', 'BitXor', 'BitAnd', 'MatMult',
           'BooleanOperator', 'BoolOp',
           'And', 'Or',
           'Comparator', 'Compare',
           'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn',
           'Keyword', 'Call', 'IfExp', 'Attribute',)

#-------------------------------------------------------------------------------

