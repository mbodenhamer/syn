from functools import partial
from syn.base_utils import compose, pyversion
from syn.python.b import Expr, from_source, MatMult
from .test_literals import examine

VER = pyversion()
eparse = compose(partial(from_source, mode='eval'), str)

#-------------------------------------------------------------------------------
# Expr

def test_expr():
    Expr

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

#-------------------------------------------------------------------------------
# Attribute

def test_attribute():
    examine('a.x')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
