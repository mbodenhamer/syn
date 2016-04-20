from nose.tools import assert_raises
from syn.type.a import Callable

#-------------------------------------------------------------------------------
# Callable

def test_callable():
    class Foo(object):
        def __call__(self):
            pass

    Foo()()
    t = Callable()
    t.check(Foo())
    t.check(test_callable)
    assert_raises(TypeError, t.validate, 1)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
