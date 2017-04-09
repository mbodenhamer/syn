import ast
from nose.tools import assert_raises
from functools import partial
from syn.python.b import Literal, from_source, from_ast, PythonNode, \
    Num, Str, Bytes, List, Tuple, Set, NameConstant
from syn.base_utils import compose
from syn.five import PY3

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

    n = Num(1)
    assert n.emit() == '1'
    assert n.emit(indent_level=1) == '    1'
    assert n.transform() is n

    rn = n.add_return()
    assert rn.emit() == 'return 1'

#-------------------------------------------------------------------------------
# Str

def test_str():
    examine("'abc'")

    s = Str('abc')
    assert s.emit() == "'abc'"
    assert s.emit(indent_level=1) == "    'abc'"
    assert s.transform() is s

#-------------------------------------------------------------------------------
# Bytes

def test_bytes():
    if PY3:
        examine("b'abc'")
        b = Bytes(b'abc')
        assert b.emit() == "b'abc'"
        assert b.emit(indent_level=1) == "    b'abc'"
        assert b.transform() is b
    else:
        examine("b'abc'", "'abc'")
        b = Bytes(b'abc')
        assert b.emit() == "'abc'"
        assert b.emit(indent_level=1) == "    'abc'"
        assert b.transform() is b

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    examine('[1, 2]')
    examine('(1, 2)')
    examine('(1,)')
    examine('{1}')

    l = List([Num(1), Num(2)])
    assert l.emit() == '[1, 2]'
    assert l.emit(indent_level=1) == '    [1, 2]'
    assert l.transform().emit() == '[1, 2]'

    t = Tuple([Num(1), Num(2)])
    assert t.emit() == '(1, 2)'
    assert t.emit(indent_level=1) == '    (1, 2)'
    assert t.transform().emit() == '(1, 2)'

    s = Set([Num(1), Num(2)])
    assert s.emit() == '{1, 2}'
    assert s.emit(indent_level=1) == '    {1, 2}'
    assert s.transform().emit() == '{1, 2}'

#-------------------------------------------------------------------------------
# NameConstant

def test_nameconstant():
    examine('True')
    examine('False')
    examine('None')

    assert NameConstant(True).emit() == 'True'
    assert NameConstant(True).emit(indent_level=1) == '    True'
    assert NameConstant(False).emit() == 'False'
    assert NameConstant(None).emit() == 'None'

    nc = NameConstant(2)
    assert_raises(TypeError, nc.validate)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
