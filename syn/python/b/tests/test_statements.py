from functools import partial
from nose.tools import assert_raises
from syn.base_utils import compose
from syn.python.b import Statement, from_source, from_ast, Pass, Num, Name, \
    Assign, Return, ProgN, Module, Alias, Import, Break, Continue

mparse = compose(partial(from_source, mode='exec'), str)

#-------------------------------------------------------------------------------
# Utilities

def examine(s, s2=None):
    if s2 is None:
        s2 = s
    tree = mparse(s)
    assert tree.emit() == s2
    tree2 = from_ast(tree.to_ast(), mode='exec')
    assert tree2.emit() == s2

#-------------------------------------------------------------------------------
# Statement

def test_statement():
    Statement

#-------------------------------------------------------------------------------
# Assign

def test_assign():
    examine('a = 1')
    examine('a = b = 1')
    examine('a, b = 1', '(a, b) = 1')

    a = Assign([Name('x')], Num(1))
    assert a.emit() == 'x = 1'
    assert a.emit(indent_level=1) == '    x = 1'

    a = Assign([Name('x'), Name('y')], Num(1))
    assert a.emit() == 'x = y = 1'
    assert a.emit(indent_level=1) == '    x = y = 1'

    a =  Assign([Name('x')], 
                ProgN(Assign([Name('y')],
                             Num(2))))
    assert a.resolve_progn() == ProgN(Assign([Name('y')], Num(2)), 
                                      Assign([Name('x')], Name('y')))
    assert Module(a).resolve_progn().emit() == 'y = 2\nx = y'

    a = Assign([Name('x')],
               Assign([Name('y')],
                      Num(2)))
    assert a.emit() == 'x = y = 2'
    assert_raises(TypeError, a.validate)
    assert Module(a).expressify_statements().resolve_progn().emit() == \
        'y = 2\nx = y'

    a = Assign([Name('x')],
               Assign([Name('y')],
                      Assign([Name('z')],
                             Num(2))))
    assert a.emit() == 'x = y = z = 2'
    assert_raises(TypeError, a.validate)
    assert Module(a).expressify_statements().resolve_progn().emit() == \
        'z = 2\ny = z\nx = y'

#-------------------------------------------------------------------------------
# Return

def test_return():
    examine('return')
    examine('return 1')

    r = Return()
    assert r.emit() == 'return'
    assert r.emit(indent_level=1) == '    return'

    r = Return(Num(1))
    assert r.emit() == 'return 1'
    assert r.emit(indent_level=1) == '    return 1'

#-------------------------------------------------------------------------------
# Import

def test_import():
    examine('import foo')
    examine('import foo, bar, baz')
    examine('import foo, bar as baz')
    examine('import foo as bar, baz')

    a = Alias('foo')
    assert a.emit() == 'foo'
    
    a = Alias('foo', 'bar')
    assert a.emit() == 'foo as bar'

    i = Import([Alias('foo'), Alias('bar', 'baz')])
    assert i.emit() == 'import foo, bar as baz'
    assert i.emit(indent_level=1) == '    import foo, bar as baz'

#-------------------------------------------------------------------------------
# Empty Statements

def test_empty_statements():
    examine('break')
    examine('continue')
    examine('pass')

    p = Pass()
    assert p.emit() == 'pass'
    rp = p.as_return()
    assert rp.emit() == 'return'

    b = Break()
    assert b.emit() == 'break'
    assert b.emit(indent_level=1) == '    break'

    c = Continue()
    assert c.emit() == 'continue'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
