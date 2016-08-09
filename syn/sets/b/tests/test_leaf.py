from nose.tools import assert_raises
from syn.sets.b import SetWrapper, NULL

SAMPLES = 10

#-------------------------------------------------------------------------------
# SetWrapper

def test_setwrapper():
    s1 = SetWrapper([1, 2, 3])
    s2 = {3, 4, 5}
    s3 = SetWrapper(s2)

    assert s1.union(s3) == SetWrapper([1,2,3,4,5])
    assert s1.union(s2) == SetWrapper([1,2,3,4,5])
    assert s1.union(s2, NULL) == SetWrapper([1,2,3,4,5])
    assert_raises(TypeError, s1.union, [3, 4])

    assert s1.intersection(s3) == SetWrapper([3])
    assert s1.intersection(s2) == SetWrapper([3])
    assert_raises(TypeError, s1.intersection, [3, 4])

    assert s1.difference(s3) == SetWrapper([1, 2])
    assert s1.difference(s2) == SetWrapper([1, 2])
    assert_raises(TypeError, s1.difference, [3, 4])

    universe = {1, 2, 3, 4, 5}
    assert s1.complement(universe) == SetWrapper([4, 5])
    assert s1.complement(SetWrapper(universe)) == SetWrapper([4,5])
    assert_raises(TypeError, s1.complement, [3, 4])

    assert s1.issubset(universe)
    assert not s1.issubset(s3)
    assert_raises(TypeError, s1.issubset, [3, 4])

    assert SetWrapper(universe).issuperset(s1)
    assert not s1.issuperset(s3)
    assert_raises(TypeError, s1.issuperset, [3, 4])

    assert s1.hasmember(3)
    assert not s1.hasmember(4)

    assert s1.simplify() is s1

    for k in range(SAMPLES):
        samp = s1.sample()
        assert s1.hasmember(samp)

    assert sorted(list(s1.enumerate())) == [1, 2, 3]
    assert s1.to_set() == {1, 2, 3}    
    assert len(list(s1.enumerate(max_enumerate = 2))) == 2

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
