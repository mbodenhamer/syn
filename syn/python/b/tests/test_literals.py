from functools import partial
from syn.python.b import Literal, from_source, from_ast
from syn.base_utils import compose

eparse = compose(partial(from_source, mode='eval'), str)
iparse = compose(partial(from_source, mode='single'), str)
mparse = compose(partial(from_source, mode='exec'), str)

#-------------------------------------------------------------------------------
# Base Class

def test_literal():
    Literal()

#-------------------------------------------------------------------------------
# Num

def test_num():
    tree = eparse(1)
    assert tree.emit() == '1'

    tree2 = from_ast(tree.to_ast(), mode='eval')
    assert tree2.emit() == '1'

    # tree3 = mparse(1)
    # assert tree3.emit() == '1'

    # tree4 = from_ast(tree.to_ast(), mode='exec')
    # assert tree4.emit() == '1'

#-------------------------------------------------------------------------------
# Str

def test_str():
    tree = eparse("'abc'")
    assert tree.emit() == "'abc'"

    tree2 = from_ast(tree.to_ast(), mode='eval')
    assert tree2.emit() == "'abc'"

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
