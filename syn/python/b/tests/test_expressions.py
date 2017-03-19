from functools import partial
from syn.base_utils import compose
from syn.python.b import Expr, from_source, from_ast

eparse = compose(partial(from_source, mode='eval'), str)

#-------------------------------------------------------------------------------
# Expr

def test_expr():
    Expr

#-------------------------------------------------------------------------------
# Binary Operators

def test_binary_operators():
    tree = eparse('1 + 2')
    assert tree.emit() == '(1 + 2)'
    tree2 = from_ast(tree.to_ast(), mode='eval')
    assert tree2.emit() == '(1 + 2)'
    
#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
