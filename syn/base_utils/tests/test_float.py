#-------------------------------------------------------------------------------
# Comparison

def test_feq():
    from syn.base_utils import feq

    assert feq(1, 1)
    assert not feq(1, 2)
    assert feq(1.0, 1.00)
    assert feq(1e-10, 2e-10, tol=1e-9)
    assert not feq(1e-10, 2e-10, tol=1e-11)

    assert feq('abc', 'abc')
    assert not feq('abc', 'ab')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
