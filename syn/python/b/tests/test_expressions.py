from functools import partial
from syn.base_utils import compose
from syn.python.b import Expr, from_source
from .test_literals import examine

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

    examine('1 + (a / 3)', '(1 + (a / 3))')
    
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
# Attribute

def test_attribute():
    examine('a.x')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
