from nose.tools import assert_raises
from syn.tagmathon.b import to_python, compile_to_python
from syn.python.b import Num

#-------------------------------------------------------------------------------
# to_python

def test_to_python():
    assert to_python(1) == Num(1)
    assert compile_to_python(()) == 'list()'
    assert_raises(TypeError, to_python, lambda x: x)
    
#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
