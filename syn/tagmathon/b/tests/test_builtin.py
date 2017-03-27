from nose.tools import assert_raises
from syn.tagmathon.b import BuiltinFunction, Variable, Add, Set, Env, eval, If

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
    
    assert_raises(TypeError, Add, 1, 2, a=1)
    assert eval(Add) == Add.name

    e = Env()
    foo = Variable('foo')
    assert eval(Set(foo, 2), e) == 'foo'
    assert e['foo'] == 2

    assert eval(If(True, 1, 2)) == 1
    assert eval(If(False, 1, 2)) == 2
    assert eval(If(False,
                   1,
                   If(True, 3, 4))) == 3
    assert eval(If(False,
                   1,
                   If(False, 3, 4))) == 4


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
