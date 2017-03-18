import ast
from nose.tools import assert_raises
from syn.python.b import PythonNode, from_ast, AstUnsupported, Context, Load

#-------------------------------------------------------------------------------
# Base Class

def test_pythonnode():
    assert sorted(PythonNode._groups['ast_attr']) == ['col_offset', 'lineno']
    assert PythonNode._groups['ast_convert_attr'] == set([])
    assert PythonNode._groups['eq_exclude'] == {'_parent'}

#-------------------------------------------------------------------------------
# Context

def test_context():
    assert Context.ast is None
    assert from_ast(ast.Load()) == Load()
    assert type(Load().to_ast()) is ast.Load
    
#-------------------------------------------------------------------------------
# Module API

def test_from_ast():
    class Foo(object):
        pass

    assert_raises(AstUnsupported, from_ast, Foo)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
