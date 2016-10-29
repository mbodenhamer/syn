from syn.five import PY2
from nose.tools import assert_raises
from syn.sets.b import Range, NULL, IntRange, StrRange
from syn.base_utils import elog, on_error

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES = max(SAMPLES, 1)

#-------------------------------------------------------------------------------
# Range

def test_range():
    r1 = Range(1, 5)
    r2 = Range(2, 5)
    
    assert r1.size() == 5

    assert r2.issubset(r1)
    assert r1.issuperset(r2)
    assert not r1.issubset(r2)
    assert not r2.issuperset(r1)

    assert r1.hasmember(3)
    assert r2.hasmember(3)
    assert r1.hasmember(4)
    assert r1.hasmember(5)
    assert not r1.hasmember(0)
    assert not r2.hasmember(1)

    for k in range(SAMPLES):
        samp = r1.sample()
        with on_error(elog, r1.hasmember, (r1, samp)):
            assert r1.hasmember(samp)

    assert sorted(list(r1.enumerate())) == [1, 2, 3, 4, 5]
    assert r1.to_set() == {1, 2, 3, 4, 5}
    assert len(list(r1.enumerate(max_enumerate = 3))) == 3

    r1.validate()
    r2.validate()
    assert_raises(ValueError, Range(2, 1).validate)

def test_range_overlap():
    r = Range(1, 4)
    assert not r.overlaps(Range(5, 6))
    assert not Range(5,6).overlaps(r)

    assert r.overlaps(Range(4, 6))
    assert Range(4,6).overlaps(r)

    assert r.overlaps(Range(3, 6))
    assert Range(3,6).overlaps(r)

    assert r.overlaps(Range(1, 6))
    assert Range(1,6).overlaps(r)

    assert r.overlaps(Range(0, 6))
    assert Range(0,6).overlaps(r)

    assert r.overlaps(Range(0, 4))
    assert Range(0,4).overlaps(r)

    assert r.overlaps(Range(0, 3))
    assert Range(0,3).overlaps(r)

    assert r.overlaps(Range(1, 3))
    assert Range(1,3).overlaps(r)

    assert r.overlaps(Range(2, 3))
    assert Range(2,3).overlaps(r)

    assert r.overlaps(Range(0, 1))
    assert Range(0,1).overlaps(r)

    assert not r.overlaps(Range(-1, 0))
    assert not Range(-1,0).overlaps(r)

def test_range_union():
    r = Range(1, 4)
    assert Range._union(NULL, NULL) == NULL
    assert Range._union(NULL, r) == r
    assert Range._union(r, NULL) == r
    assert r.union(NULL) == (r, (NULL,))
    assert r.union(NULL, NULL) == (r, (NULL, NULL))

    assert r.union(Range(5, 6)) == (r, (Range(5, 6),))
    assert Range(5, 6).union(r) == (Range(5, 6), (r,))
    assert r.union(Range(4,5), Range(5,6)) == (Range(1, 6), ())

    assert r.union(Range(4, 6)) == (Range(1, 6), ())
    assert Range(4, 6).union(r) == (Range(1, 6), ())

    assert r.union(Range(2, 5)) == (Range(1, 5), ())
    assert Range(2, 5).union(r) == (Range(1, 5), ())

    assert r.union(Range(2, 3)) == (Range(1, 4), ())
    assert Range(2, 3).union(r) == (Range(1, 4), ())

def test_range_intersection():
    r = Range(1, 4)
    assert r.intersection(NULL) is NULL

    assert r.intersection(Range(5, 6)) is NULL
    assert Range(5, 6).intersection(r) is NULL

    assert r.intersection(Range(4, 6)) == Range(4, 4)
    assert Range(4, 6).intersection(r) == Range(4, 4)

    assert r.intersection(Range(2, 5)) == Range(2, 4)
    assert Range(2, 5).intersection(r) == Range(2, 4)

    assert r.intersection(Range(2, 3)) == Range(2, 3)
    assert Range(2, 3).intersection(r) == Range(2, 3)

def test_range_difference():
    r = Range(1, 4)
    assert r.difference(NULL) == (r, None)

    assert r.difference(Range(5, 6)) == (r, None)
    assert Range(5, 6).difference(r) == (Range(5, 6), None)

    assert r.difference(Range(4, 6)) == (Range(1, 3), None)
    assert Range(4, 6).difference(r) == (Range(5, 6), None)

    assert r.difference(Range(2, 5)) == (Range(1, 1), None)
    assert Range(2, 5).difference(r) == (Range(5, 5), None)

    assert r.difference(Range(2, 3)) == (Range(1, 1), Range(4, 4))
    assert Range(2, 3).difference(r) == (NULL, None)

    assert r.complement(Range(3, 7)) == (Range(5, 7), None)

#-------------------------------------------------------------------------------
# IntRange

def test_intrange():
    i = IntRange(1, 4)
    assert i.hasmember(1)
    assert i.hasmember(4)
    assert not i.hasmember(5)
    if PY2:
        assert not i.hasmember(long(3))

#-------------------------------------------------------------------------------
# StrRange

def test_strrange():
    s = StrRange('a', u'c')
    assert s.lb == 97
    assert s.ub == 99

    assert s.hasmember('a')
    assert s.hasmember(u'a')
    assert not s.hasmember('d')
    assert_raises(TypeError, s.hasmember, 97)

    for k in range(SAMPLES):
        item = s.sample()
        with on_error(elog, s.hasmember, (s, item)):
            assert s.hasmember(item)

    assert sorted(s.enumerate()) == ['a', 'b', 'c']
    assert s.to_set() == {'a', 'b', 'c'}

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
