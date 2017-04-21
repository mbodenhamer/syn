from functools import partial
from nose.tools import assert_raises
from syn.base_utils import compose, pyversion
from syn.python.b import Expr, from_source, MatMult, Call, Name, BinOp, \
    Add, Assign, Module, Num, Return
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

    #assert p2r.emit() == 'x = 5\nreturn (x + 2)'

    # p3 = Module(BinOp(Assign([Name('x')],
    #                          BinOp(Assign([Name('y')],
    #                                       Num(5)),
    #                                Add(),
    #                                Num(1))),
    #                   Add(),
    #                   Num(2)))
    # assert p3.emit() == '(x = (y = 5 + 1) + 2)'
    # assert_raises(TypeError, p3.validate)
    # p3r = p3.expressify_statements().resolve_progn()
    # assert p3r.emit() == 'y = 5\nx = (y + 1)\n(x + 2)'

#-------------------------------------------------------------------------------
# Boolean Operators

def test_boolean_operators():
    examine('(a and b)')
    examine('(a or b)')
    examine('(a or b or c or d)')

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

#-------------------------------------------------------------------------------
# IfExp

def test_ifexp():
    examine('(a if b else c)')

#-------------------------------------------------------------------------------
# Attribute

def test_attribute():
    examine('a.x')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
