from nose.tools import assert_raises
from syn.five import xrange, PY2

SAMPLES = 20
from syn.base_utils.rand import MIN_FLOAT

#-------------------------------------------------------------------------------
# Numeric

def test_rand_bool():
    from syn.base_utils import rand_bool

    bools = [rand_bool() for k in xrange(SAMPLES)]
    assert all(isinstance(s, bool) for s in bools)

def test_randint():
    from syn.base_utils import rand_int

    ints = [rand_int() for k in xrange(SAMPLES)]
    assert all(isinstance(i, int) for i in ints)
    assert any(i != 0 for i in ints)

def test_randlong():
    from syn.base_utils import rand_long

    if PY2:
        longs = [rand_long() for k in xrange(SAMPLES)]
        assert all(isinstance(l, long) for l in longs)
        assert any(l != 0 for l in longs)

def test_randfloat():
    from syn.base_utils import rand_float
    
    floats = [rand_float() for k in xrange(SAMPLES)]
    assert all(isinstance(f, float) for f in floats)
    assert any(f != 0 for f in floats)

    floats = [rand_float(ub = 3) for k in xrange(SAMPLES)]
    assert all(MIN_FLOAT <= f <= 3 for f in floats)

    floats = [rand_float(2, 3) for k in xrange(SAMPLES)]
    assert all(2 <= f <= 3 for f in floats)

def test_rand_complex():
    from syn.base_utils import rand_complex

    comps = [rand_complex() for k in xrange(SAMPLES)]
    assert all(isinstance(s, complex) for s in comps)

    comps = [rand_complex(imag_only=True) for k in xrange(SAMPLES)]
    assert all(isinstance(s, complex) for s in comps)
    assert all(s.real == 0 for s in comps)

#-------------------------------------------------------------------------------
# String

def test_randstr():
    from syn.base_utils import rand_str

    strs = [rand_str() for k in range(SAMPLES)]
    assert all(isinstance(s, str) for s in strs)
    assert any(len(s) > 0 for s in strs)


def test_rand_unicode():
    from syn.base_utils import rand_unicode

    if PY2:
        strs = [rand_unicode(min_len=1) for k in range(SAMPLES)]
        assert all(isinstance(s, unicode) for s in strs)
        assert any(len(s) > 0 for s in strs)

#-------------------------------------------------------------------------------
# Misc

def test_rand_none():
    from syn.base_utils import rand_none

    nones = [rand_none() for k in range(SAMPLES)]
    assert all(s is None for s in nones)

#-------------------------------------------------------------------------------
# Dispatch

def test_rand_dispatch():
    from syn.base_utils import rand_dispatch

    assert isinstance(rand_dispatch(int), int)
    assert isinstance(rand_dispatch(float), float)
    assert isinstance(rand_dispatch(complex), complex)
    assert isinstance(rand_dispatch(str), str)
    assert isinstance(rand_dispatch(bool), bool)
    
    if PY2:
        assert isinstance(rand_dispatch(long), long)
        assert isinstance(rand_dispatch(unicode), (str, unicode))

    class Foo(object): pass
    assert_raises(TypeError, rand_dispatch, Foo)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
