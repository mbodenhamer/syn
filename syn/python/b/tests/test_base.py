import ast
from nose.tools import assert_raises
from syn.python.b import PythonNode, from_ast, AstUnsupported, Context, Load, \
    Special, PythonError, ProgN, Assign, Num, Name

#-------------------------------------------------------------------------------
# Utilities

def test_is_expression_type():
    from syn.python.b.base import is_expression_type
    assert_raises(PythonError, is_expression_type, 1)

#-------------------------------------------------------------------------------
# Utility Classes

def test_gensym():
    from syn.python.b.base import GenSym

    g = GenSym({'a', 'b'})
    assert g.names == {'a', 'b'}
    assert g.counter.peek() == -1
    gen = g.generate()
    assert gen == '_gensym_0'
    assert g.names == {'a', 'b', '_gensym_0'}
    assert g.counter.peek() == 0
    gen2 = g.generate()
    assert gen2 == '_gensym_1'
    assert g.names == {'a', 'b', '_gensym_0', '_gensym_1'}
    assert g.counter.peek() == 1

    g2 = GenSym({'a', '_gensym_0'})
    gen = g2.generate()
    assert gen == '_gensym_1'
    assert g2.names == {'a', '_gensym_0', '_gensym_1'}
    assert g2.counter.peek() == 1

    g2.update({'b'})
    assert g2.names == {'a', 'b', '_gensym_0', '_gensym_1'}
    assert g2.counter.peek() == 1

#-------------------------------------------------------------------------------
# Base Class

def test_pythonnode():
    assert sorted(PythonNode._groups['ast_attr']) == ['col_offset', 'lineno']
    assert PythonNode._groups['ast_convert_attr'] == set([])
    assert PythonNode._groups['eq_exclude'] == {'_parent'}

    assert PythonNode.minver == '0'
    assert PythonNode.maxver == '100'

    p = PythonNode()
    assert_raises(NotImplementedError, p.emit)

#-------------------------------------------------------------------------------
# Context

def test_context():
    assert Context.ast is None
    assert from_ast(ast.Load()) == Load()
    assert type(Load().to_ast()) is ast.Load
    
#-------------------------------------------------------------------------------
# Special

def test_special():
    s = Special()
    assert_raises(PythonError, s.validate)

def test_progn():
    p = ProgN()
    assert_raises(PythonError, p.validate)
    assert_raises(PythonError, p.value)
    assert_raises(PythonError, p.valuify)
    # assert_raises(NotImplementedError, p.as_value)
    assert_raises(NotImplementedError, p.expressify_statements)

    p = ProgN(Assign([Name('x')], Num(2)))
    assert p.valuify() is p
    assert p.value() == Name('x')

    ppp = ProgN(Num(1),
                ProgN(Num(2),
                      ProgN(Num(3)),
                      ProgN(Assign([Name('y')], Num(4)))))
    assert ppp.value() == Name('y')
    assert ppp.resolve_progn() == ProgN(Num(1), 
                                        Num(2), 
                                        Num(3), 
                                        Assign([Name('y')], Num(4)))

    p = ProgN(Num(2))
    assert_raises(PythonError, p.value)
    pv = p.valuify()
    assert pv == ProgN(Assign([Name('_gensym_0')], Num(2)))
    assert pv.value() == Name('_gensym_0')

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
