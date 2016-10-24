from nose.tools import assert_raises
from syn.five import range
from syn.base_utils import rand_int, on_error, elog
from syn.globals import TEST_SAMPLES as SAMPLES

SAMPLES = max(SAMPLES, 1)

#-------------------------------------------------------------------------------
# Query

def test_iterlen():
    from syn.base_utils import iterlen, is_empty
    l = range(10)
    assert iterlen(l) == 10
    i = iter(l)
    assert_raises(TypeError, len, i)
    assert iterlen(i) == 10
    assert not is_empty(i)
    assert iterlen(i) == 10

#-------------------------------------------------------------------------------
# Modification

def test_consume():
    from syn.base_utils import consume, is_empty

    lst = range(10)
    i1 = iter(lst)
    consume(i1, 4)
    lst2 = list(i1)
    assert lst2 == range(4, 10)
    consume(i1)
    assert is_empty(i1)

def test_first():
    from syn.base_utils import first, iterlen

    l = range(10)
    assert first(l) == 0
    assert l == range(10)

    i = iter(l)
    assert first(i) == 0
    assert first(i) == 1
    assert iterlen(i) == 8

def test_last():
    from syn.base_utils import last, is_empty

    l = range(10)
    i = iter(l)
    assert last(i) == 9
    assert is_empty(i)

#-------------------------------------------------------------------------------
# Calculation

def test_iteration_length():
    from syn.base_utils import iteration_length

    assert iteration_length(5) == 5
    assert iteration_length(5, 0) == 5
    assert iteration_length(5, 1) == 4
    assert iteration_length(5, 0, 2) == 3

    for k in range(SAMPLES):
        N = rand_int(0, 20)
        start = rand_int(0, 20)
        step = rand_int(1, 5)
        
        with on_error(elog, iteration_length, (N, start, step)):
            assert iteration_length(N, start, step) == \
                len(list(range(start, N, step)))

    assert iteration_length(0) == 0
    assert iteration_length(10, 10) == 0
    assert iteration_length(10, 20) == 0
    assert_raises(ValueError, iteration_length, -1)
    assert_raises(ValueError, iteration_length, 10, 20, -1)

    assert iteration_length(10, -1, 1) == 1
    assert iteration_length(10, -1, 10) == 1

    assert iteration_length(10, -1, -1) == 10
    assert iteration_length(10, -1, -3) == 4
    assert iteration_length(10, 1, 3) == 3
    assert iteration_length(10, 5, -1) == 6

    assert_raises(ValueError, iteration_length, 10, -11)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
