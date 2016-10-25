from nose.tools import assert_raises
from syn.five import xrange, PY2, PY3

from syn.base_utils.rand import MIN_FLOAT, PRIMITIVE_TYPES
from syn.base_utils import is_hashable, ngzwarn, on_error, elog

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLESII = SAMPLES // 2
SAMPLESIII = SAMPLES // 5

SAMPLES = max(SAMPLES, 1)
SAMPLESII = max(SAMPLESII, 1)
SAMPLESIII = max(SAMPLESIII, 1)
ngzwarn(SAMPLES, 'SAMPLES')
ngzwarn(SAMPLES, 'SAMPLESII')
ngzwarn(SAMPLES, 'SAMPLESIII')

#-------------------------------------------------------------------------------
# Numeric

def test_rand_bool():
    from syn.base_utils import rand_bool

    bools = [rand_bool() for k in xrange(SAMPLESIII)]
    assert all(isinstance(s, bool) for s in bools)

def test_randint():
    from syn.base_utils import rand_int

    ints = [rand_int() for k in xrange(SAMPLESII)]
    assert all(isinstance(i, int) for i in ints)
    if len(ints) > 2:
        assert any(i != 0 for i in ints)

def test_randlong():
    from syn.base_utils import rand_long

    if PY2:
        longs = [rand_long() for k in xrange(SAMPLESII)]
        assert all(isinstance(l, long) for l in longs)
        if len(longs) > 2:
            assert any(l != 0 for l in longs)

def test_randfloat():
    from syn.base_utils import rand_float
    
    floats = [rand_float() for k in xrange(SAMPLESII)]
    assert all(isinstance(f, float) for f in floats)
    if len(floats) > 2:
        assert any(f != 0 for f in floats)

    floats = [rand_float(ub = 3) for k in xrange(SAMPLESII)]
    assert all(MIN_FLOAT <= f <= 3 for f in floats)

    floats = [rand_float(2, 3) for k in xrange(SAMPLESII)]
    assert all(2 <= f <= 3 for f in floats)

def test_rand_complex():
    from syn.base_utils import rand_complex

    comps = [rand_complex() for k in xrange(SAMPLESIII)]
    assert all(isinstance(s, complex) for s in comps)

    comps = [rand_complex(imag_only=True) for k in xrange(SAMPLESII)]
    assert all(isinstance(s, complex) for s in comps)
    assert all(s.real == 0 for s in comps)

#-------------------------------------------------------------------------------
# String

def test_randstr():
    from syn.base_utils import rand_str

    strs = [rand_str() for k in xrange(SAMPLESII)]
    assert all(isinstance(s, str) for s in strs)
    if len(strs) > 2:
        assert any(len(s) > 0 for s in strs)


def test_rand_unicode():
    from syn.base_utils import rand_unicode

    if PY2:
        strs = [rand_unicode(min_len=1) for k in xrange(SAMPLESII)]
        assert all(isinstance(s, unicode) for s in strs)
        if len(strs) > 2:
            assert any(len(s) > 0 for s in strs)

def test_rand_bytes():
    from syn.base_utils import rand_bytes
    
    if PY3:
        bytess = [rand_bytes() for k in xrange(SAMPLESII)]
        assert all(isinstance(b, bytes) for b in bytess)

#-------------------------------------------------------------------------------
# Sequence

def test_rand_list():
    from syn.base_utils import rand_list, is_flat

    lists = [rand_list() for k in xrange(SAMPLESIII)]
    assert all(isinstance(l, list) for l in lists)

    for k in xrange(SAMPLESII):
        l = rand_list(max_depth=0)

        with on_error(elog, is_flat, (l,)):
            assert is_flat(l)

def test_rand_tuple():
    from syn.base_utils import rand_tuple

    tuples = [rand_tuple() for k in xrange(SAMPLESIII)]
    assert all(isinstance(t, tuple) for t in tuples)

#-------------------------------------------------------------------------------
# Mapping

def test_rand_dict():
    from syn.base_utils import rand_dict

    dicts = [rand_dict() for k in xrange(SAMPLESIII)]
    assert all(isinstance(d, dict) for d in dicts)

#-------------------------------------------------------------------------------
# Set

def test_rand_set():
    from syn.base_utils import rand_set

    sets = [rand_set() for k in xrange(SAMPLESIII)]
    assert all(isinstance(s, set) for s in sets)
    
def test_rand_frozenset():
    from syn.base_utils import rand_frozenset

    sets = [rand_frozenset() for k in xrange(SAMPLESIII)]
    assert all(isinstance(s, frozenset) for s in sets)

#-------------------------------------------------------------------------------
# Misc

def test_rand_none():
    from syn.base_utils import rand_none

    nones = [rand_none() for k in range(SAMPLESIII)]
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
    assert isinstance(rand_dispatch(list), list)
    assert isinstance(rand_dispatch(tuple), tuple)
    assert isinstance(rand_dispatch(dict), dict)
    assert isinstance(rand_dispatch(set), set)
    assert isinstance(rand_dispatch(frozenset), frozenset)
    assert rand_dispatch(type(None)) is None
    
    if PY2:
        assert isinstance(rand_dispatch(long), long)
        assert isinstance(rand_dispatch(unicode), (str, unicode))

    if PY3:
        assert isinstance(rand_dispatch(bytes), bytes)

    class Bar(object):
        @classmethod
        def _generate(cls, **kwargs):
            return cls()

    assert isinstance(rand_dispatch(Bar), Bar)

    class Foo(object): pass
    assert_raises(TypeError, rand_dispatch, Foo)

def test_rand_primitive():
    from syn.base_utils import rand_primitive

    for k in xrange(SAMPLESII):
        x = rand_primitive()
        assert isinstance(x, tuple(PRIMITIVE_TYPES))

def test_rand_hashable():
    from syn.base_utils import rand_hashable

    for k in xrange(SAMPLES):
        x = rand_hashable()

        with on_error(elog, is_hashable, (x,)):
            assert is_hashable(x)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
