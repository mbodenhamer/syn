from nose.tools import assert_raises
from syn.tagmathon.b import SyntagmathonNode, Variable, Env, eval

#-------------------------------------------------------------------------------
# Base Class

def test_syntagmathonnode():
    s = SyntagmathonNode()
    assert_raises(NotImplementedError, s.eval, None)
    assert_raises(NotImplementedError, s.to_python, None)

#-------------------------------------------------------------------------------
# Variable

def test_variable():
    v = Variable('foo')
    e = Env()
    e['foo'] = 3
    assert eval(v, e) == 3

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
