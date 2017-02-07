import math

#-------------------------------------------------------------------------------
# Comparison

def test_feq():
    from syn.base_utils import feq

    assert feq(1, 1)
    assert feq(1, 1.0)
    assert not feq(1, 2)
    assert not feq(1, 0.9)
    assert feq(1.0, 1.00)
    assert feq(1e-10, 2e-10, tol=1e-9)
    assert not feq(1e-10, 2e-10, tol=1e-11)

    assert not feq(1.0001, 1.0002, tol = 1e-5)
    assert feq(1.00001, 1.00002, tol = 1e-5)
    assert not feq(1.00001e300, 1.00002e300, tol = 1e-5)
    assert feq(1.00001e300, 1.00002e300, tol = 1e-5, relative=True)
    assert not feq(1.0001e300, 1.0002e300, tol = 1e-5, relative=True)
    assert not feq(1, 2, relative=True)

    assert feq('abc', 'abc')
    assert not feq('abc', 'ab')

def test_cfeq():
    from syn.base_utils import cfeq

    assert cfeq(1+1j, 1.001+1.001j, tol=0.01)
    assert not cfeq(1+1j, 1.001+1.001j)
    assert not cfeq(1, 1.001+1.001j, tol=0.01)

    assert cfeq('abc', 'abc')
    assert not cfeq('abc', 'ab')

#-------------------------------------------------------------------------------
# Math

def test_prod():
    from syn.base_utils import prod, feq

    assert prod([2, 3, 4]) == 24
    assert feq(prod([2, 3, 4], log=True), 24)

    assert prod(range(1, 21)) == math.factorial(20)

def test_sgn():
    from syn.base_utils import sgn

    assert sgn(-0.000000005) == -1
    assert sgn(0.000000005) == 1
    assert sgn(0.0) == 0

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
