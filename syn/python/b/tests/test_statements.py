from functools import partial
from syn.base_utils import compose
from syn.python.b import Statement, from_source, from_ast

mparse = compose(partial(from_source, mode='exec'), str)

#-------------------------------------------------------------------------------
# Statement

def test_statement():
    Statement

#-------------------------------------------------------------------------------
# Assign

def test_assign():
    tree = mparse('a = 1')
    assert tree.emit() == 'a = 1'
    tree2 = from_ast(tree.to_ast(), mode='exec')
    assert tree2.emit() == 'a = 1'


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
