import ast
from nose.tools import assert_raises
from functools import partial
from syn.python.b import Literal, from_source, from_ast, PythonNode
from syn.base_utils import compose

eparse = compose(partial(from_source, mode='eval'), str)
iparse = compose(partial(from_source, mode='single'), str)
mparse = compose(partial(from_source, mode='exec'), str)

#-------------------------------------------------------------------------------
# Utilities

def examine(s, s2=None):
    if s2 is None:
        s2 = s
    tree = eparse(s)
    assert tree.emit() == s2
    tree2 = from_ast(tree.to_ast(), mode='eval')
    assert tree2.emit() == s2

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

    tree3 = mparse(1)
    assert tree3.emit() == '1'
    tree4 = from_ast(tree3.to_ast(), mode='exec')
    assert tree4.emit() == '1'

    tree5 = iparse(1)
    assert tree5.emit() == '1'
    tree6 = from_ast(tree5.to_ast(), mode='single')
    assert tree6.emit() == '1'

    tree7 = tree3.abstract()
    assert any(n.lineno is not None for n in tree3.nodes)
    assert all(n.lineno is None for n in tree7.nodes)

    from syn.python.b import Num as Num_
    import syn.python.b.base as pybbase

    def bad():
        class Num(PythonNode):
            pass

    assert_raises(TypeError, bad)
    assert pybbase.AST_REGISTRY[ast.Num] is Num_

#-------------------------------------------------------------------------------
# Str

def test_str():
    examine("'abc'")

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    examine('[1, 2]')
    examine('(1, 2)')
    examine('(1,)')
    examine('{1}')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
