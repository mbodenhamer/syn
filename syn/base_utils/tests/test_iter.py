from nose.tools import assert_raises
from syn.five import range

#-------------------------------------------------------------------------------

def test_iterlen():
    from syn.base_utils import iterlen, is_empty
    l = range(10)
    assert iterlen(l) == 10
    i = iter(l)
    assert_raises(TypeError, len, i)
    assert iterlen(i) == 10
    assert not is_empty(i)
    assert iterlen(i) == 10

def test_consume():
    from syn.base_utils import consume, is_empty

    lst = range(10)
    i1 = iter(lst)
    consume(i1, 4)
    lst2 = list(i1)
    assert lst2 == range(4, 10)
    consume(i1)
    assert is_empty(i1)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
