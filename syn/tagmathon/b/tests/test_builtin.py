from nose.tools import assert_raises
from syn.tagmathon.b import BuiltinFunction, Variable, Add, Set, Env, eval, \
    If, compile_to_python, LE, Eq, Assert

#-------------------------------------------------------------------------------
# BuiltinFunction

def test_builtinfunction():
    BuiltinFunction

#-------------------------------------------------------------------------------
# Builtins

def test_builtins():
    assert eval(Add(1, 2)) == 3
    assert eval(Add(1, b=2)) == 3
    assert eval(Add(a=1, b=2)) == 3
    
    assert compile_to_python(Add(1, 2)) == '(1 + 2)'
    assert compile_to_python(Add(1, b=2)) == '(1 + 2)'
    assert compile_to_python(Add(a=1, b=2)) == '(1 + 2)'

    assert_raises(TypeError, Add, 1, 2, a=1)
    assert eval(Add) is Add

    e = Env()
    foo = Variable('foo')
    assert eval(Set(foo, 2), e) == 2
    assert compile_to_python(Set(foo, 2)) == 'foo = 2'
    assert e['foo'] == 2

    assert eval(If(True, 1, 2)) == 1
    assert compile_to_python(If(True, 1, 2)) == 'if True:\n    1\nelse:\n    2'
    assert eval(If(False, 1, 2)) == 2
    assert eval(If(False,
                   1,
                   If(True, 3, 4))) == 3
    assert eval(If(False,
                   1,
                   If(False, 3, 4))) == 4
    assert compile_to_python(If(False,
                                1,
                                If(False, 3, 4))) == '''if False:
    1
else:
    if False:
        3
    else:
        4'''
    
    assert eval(LE(1, 2)) is True
    assert eval(LE(2, 1)) is False
    assert compile_to_python(LE(1, 2)) == '(1 <= 2)'

    assert eval(Eq(1, 1)) is True
    assert eval(Eq(1, 2)) is False
    assert compile_to_python(Eq(1, 2)) == '(1 == 2)'
    
    eval(Assert(Eq(1, 1)))
    assert_raises(AssertionError, eval, Assert(Eq(1, 2)))
    assert_raises(NotImplementedError, compile_to_python, Assert(Eq(1, 2)))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
