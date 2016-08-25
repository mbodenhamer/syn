from syn.five import range, xrange

#-------------------------------------------------------------------------------
# range

def test_range():
    r = range(5)
    assert isinstance(r, list)
    assert r == [0, 1, 2, 3, 4]

    xr = xrange(5)
    assert not isinstance(xr, list)
    assert list(xr) == r

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
