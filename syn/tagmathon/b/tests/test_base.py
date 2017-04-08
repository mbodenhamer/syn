from nose.tools import assert_raises
from syn.base_utils import assert_equivalent
from syn.tagmathon.b import SyntagmathonNode, Variable, Env, eval, \
    compile_to_python, vars

#-------------------------------------------------------------------------------
# Base Class

def test_syntagmathonnode():
    s = SyntagmathonNode()
    assert_raises(NotImplementedError, s.eval, None)
    assert_raises(NotImplementedError, s.to_python)

#-------------------------------------------------------------------------------
# Variable

def test_variable():
    v = Variable('foo')
    e = Env()
    e['foo'] = 3
    assert eval(v, e) == 3
    assert compile_to_python(v) == 'foo'

#-------------------------------------------------------------------------------
# Utilities

def test_vars():
    a, b = vars('a', 'b')
    assert_equivalent(a, Variable('a'))
    assert_equivalent(b, Variable('b'))

    c = vars('c')
    assert_equivalent(c, Variable('c'))

    d, e = vars('d e')
    assert_equivalent(d, Variable('d'))
    assert_equivalent(e, Variable('e'))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
