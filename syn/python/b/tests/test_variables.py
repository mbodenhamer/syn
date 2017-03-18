from syn.python.b import Name, from_source, from_ast
from functools import partial
from syn.base_utils import compose

eparse = compose(partial(from_source, mode='eval'), str)

#-------------------------------------------------------------------------------
# Name

def test_name():
    tree = eparse('foo')
    assert tree.emit() == 'foo'
    tree2 = from_ast(tree.to_ast(), mode='eval')
    assert tree2.emit() == 'foo'

    assert tree.abstract().root[0] == Name('foo', _id=1)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
