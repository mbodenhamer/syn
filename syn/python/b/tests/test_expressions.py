from functools import partial
from nose.tools import assert_raises
from syn.base_utils import compose, pyversion
from syn.python.b import Expr, from_source, MatMult, Call, Name, BinOp, \
    Add, Assign, Module, Num, Return, UnaryOp, USub, Not, And, Or, BoolOp, \
    Compare, Lt, LtE, Keyword, Starred, IfExp, Attribute
from syn.util.log.b import Logger
from .test_literals import examine

VER = pyversion()
eparse = compose(partial(from_source, mode='eval'), str)

#-------------------------------------------------------------------------------
# Expr

def test_expr():
    e = Expr(Num(1))
    assert e.emit() == '1'
    assert e.emit(indent_level=1) == '    1'

    assert e._children == [Num(1)]
    assert e._node_count == 2
    e._set_child(0, Num(2))
    assert e.emit() == '2'
    assert e._children == [Num(2)]
    assert e._node_count == 2

#-------------------------------------------------------------------------------
# Unary Operators

def test_unary_operators():
    examine('+a')
    examine('-a')
    examine('(not a)')
    examine('~a')

    e = UnaryOp(USub(), Name('x'))
    assert e.emit() == '-x'
    assert e.emit(indent_level=1) == '    -x'

    e = UnaryOp(Not(), Name('x'))
    assert e.emit() == '(not x)'
    assert e.emit(indent_level=1) == '    (not x)'

#-------------------------------------------------------------------------------
# Binary Operators

def test_binary_operators():
    examine('(a + 1)')
    examine('(a - 1)')
    examine('(a * 1)')
    examine('(a / 1)')
    examine('(a // 1)')
    examine('(a % 1)')
    examine('(a ** 1)')
    examine('(a << 1)')
    examine('(a >> 1)')
    examine('(a | 1)')
    examine('(a ^ 1)')
    examine('(a & 1)')

    if VER >= MatMult.minver:
        examine('(a @ b)')

    examine('1 + (a / 3)', '(1 + (a / 3))')
    
    p1 = Module(BinOp(Assign([Name('x')], Num(5)),
                      Add(),
                      Num(2)))
    assert p1.emit() == '(x = 5 + 2)'
    assert_raises(TypeError, p1.validate) # Indeed, this is not valid python
    p1r = p1.expressify_statements().resolve_progn()
    p1r.validate()
    assert p1r.emit() == 'x = 5\n(x + 2)'

    lgr = Logger()
    p2 = Module(Return(BinOp(Assign([Name('x')], Num(5)),
                             Add(),
                             Num(2))))
    assert p2.emit() == 'return (x = 5 + 2)'
    assert_raises(TypeError, p2.validate)
    p2ex = p2.expressify_statements(logger=lgr)
    p2r = p2ex.resolve_progn(logger=lgr)

    for depth, event in lgr.root[1].depth_first(yield_depth=True):
        print('-' * 80)
        print(event.display(depth))

    p2r.validate()
    assert p2r.emit() == 'x = 5\n_gensym_0 = (x + 2)\nreturn _gensym_0'

    p3 = Module(Return(BinOp(Assign([Name('x')],
                                    BinOp(Assign([Name('y')],
                                                 Num(5)),
                                          Add(),
                                          Num(1))),
                             Add(),
                             Num(2))))
    assert p3.emit() == 'return (x = (y = 5 + 1) + 2)'
    assert_raises(TypeError, p3.validate)
    p3r = p3.expressify_statements().resolve_progn()
    p3r.validate()
    assert p3r.emit() == '''y = 5
_gensym_0 = (y + 1)
x = _gensym_0
_gensym_1 = (x + 2)
return _gensym_1'''

#-------------------------------------------------------------------------------
# Boolean Operators

def test_boolean_operators():
    examine('(a and b)')
    examine('(a or b)')
    examine('(a or b or c or d)')

    e = BoolOp(And(), [Name('a'), Name('b'), Num(1)])
    assert e.emit() == '(a and b and 1)'
    assert e.emit(indent_level=1) == '    (a and b and 1)'

    e = BoolOp(Or(), [Name('a'), Name('b'), Num(1)])
    assert e.emit() == '(a or b or 1)'

#-------------------------------------------------------------------------------
# Compare

def test_compare():
    examine('(1 == 2)')
    examine('(1 != 2)')
    examine('(1 < 2)')
    examine('(1 <= 2)')
    examine('(1 > 2)')
    examine('(1 >= 2)')
    examine('(a is b)')
    examine('(a is not b)')
    examine('(a in b)')
    examine('(a not in b)')

    examine('(a < 1 >= 2 <= c is not d)')

    e = Compare(Name('x'),
                [Lt(), LtE()],
                [Name('y'), Num(2)])
    assert e.emit() == '(x < y <= 2)'
    assert e.emit(indent_level=1) == '    (x < y <= 2)'

#-------------------------------------------------------------------------------
# Call

def test_call():
    examine('foo()')
    examine('foo(1)')
    examine('foo(1, 2, 3)')
    examine('foo(a=1, b=2)')
    examine('foo(1, 2, **d)')
    if VER < '3.5':
        examine('foo(a=2, *c)')
    else:
        examine('foo(*c, a=2)')
    examine('foo(*c)')
    examine('foo(**d)')
    examine('foo(1, a=2, **b)')
    if VER < '3.5':
        examine('foo(1, 2, a=3, b=4, *c, **d)')
    else:
        examine('foo(1, 2, *c, a=3, b=4, **d)')

    assert Call(Name('list')).emit() == 'list()'
    
    c1 = Call(Name('c1'),
              [Num(2),
               Assign([Name('x')],
                      Num(3)),
               Assign([Name('y')],
                      Num(4))])
    assert c1.emit() == 'c1(2, x = 3, y = 4)'
    assert_raises(TypeError, c1.validate)
    c1r = Module(c1).expressify_statements().resolve_progn()
    c1r.emit()
    assert c1r.emit() == 'x = 3\ny = 4\nc1(2, x, y)'

    k = Keyword('foo', Num(1))
    assert k.emit() == 'foo=1'
    
    if VER >= '3.5':
        k = Keyword(None, Name('x'))
        assert k.emit() == '**x'

    if VER < '3.5':
        c = Call(Name('foo'),
                 [Num(1), Num(2)],
                 [Keyword('a', Num(3)), Keyword('b', Num(4))],
                 Name('c'),
                 Name('d'))
        assert c.emit() == 'foo(1, 2, a=3, b=4, *c, **d)'
        assert c.emit(indent_level=1) == '    foo(1, 2, a=3, b=4, *c, **d)'
    else:
        c = Call(Name('foo'),
                 [Num(1), Num(2), Starred(Name('c'))],
                 [Keyword('a', Num(3)), 
                  Keyword('b', Num(4)), 
                  Keyword(None, Name('d'))])
        assert c.emit() == 'foo(1, 2, *c, a=3, b=4, **d)'
        assert c.emit(indent_level=1) == '    foo(1, 2, *c, a=3, b=4, **d)'

    c = Call(Name('foo'))
    assert c.emit() == 'foo()'

#-------------------------------------------------------------------------------
# IfExp

def test_ifexp():
    examine('(a if b else c)')
    
    e = IfExp(Name('a'), Name('b'), Name('c'))
    assert e.emit() == '(b if a else c)'
    assert e.emit(indent_level=1) == '    (b if a else c)'

#-------------------------------------------------------------------------------
# Attribute

def test_attribute():
    examine('a.x')

    e = Attribute(Name('foo'), 'bar')
    assert e.emit() == 'foo.bar'
    assert e.emit(indent_level=1) == '    foo.bar'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
