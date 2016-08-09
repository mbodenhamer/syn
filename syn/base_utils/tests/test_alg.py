from functools import reduce

#-------------------------------------------------------------------------------
# defer_reduce

def test_defer_reduce():
    from syn.base_utils import defer_reduce
    from operator import add

    true = lambda *args: True
    xs = list(range(10))
    assert defer_reduce(add, xs, true) == (reduce(add, xs), [])

    silly = lambda item, accum: item > 5 or accum > 10
    assert defer_reduce(add, xs, silly, 0) == (reduce(add, xs), [])

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
