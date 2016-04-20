from nose.tools import assert_raises
from syn.type.a.ext import Callable, List

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
    t.check(int)
    t.validate(int)
    assert_raises(TypeError, t.check, 1)
    assert_raises(TypeError, t.validate, 1)

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    int_list = List(int)

    assert int_list.query([1, 2, 3])
    assert not int_list.query([1.2, 2, 3])
    assert not int_list.query((1, 2, 3))

    bad_list = (1.2, '3', 4)
    good_list = [1, 2, 3]
    assert int_list.coerce(bad_list) == [1, 3, 4]
    assert int_list.coerce(good_list) is good_list

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
