from nose.tools import assert_raises
from syn.sets.b import SetWrapper, NULL, TypeWrapper, ClassWrapper, Empty
from syn.base_utils import rand_int

SAMPLES = 10

#-------------------------------------------------------------------------------
# SetWrapper

def test_setwrapper():
    s1 = SetWrapper([1, 2, 3])
    s2 = {3, 4, 5}
    s3 = SetWrapper(s2)

    assert s1.size() == s3.size() == 3
    assert s1.size_limits() == (3, 3)

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

    for k in range(SAMPLES):
        samp = s1.sample()
        assert s1.hasmember(samp)

    item = s1.get_one()
    assert s1.hasmember(item)

    assert sorted(list(s1.enumerate())) == [1, 2, 3]
    assert s1.to_set() == {1, 2, 3}    
    assert len(list(s1.enumerate(max_enumerate = 2))) == 2

#-------------------------------------------------------------------------------
# TypeWrapper

def test_typewrapper():
    tw = TypeWrapper(int)

    assert tw.size() == float('inf')
    
    for k in range(SAMPLES):
        item = tw.sample()
        assert tw.hasmember(item)

    twlist = list(tw.enumerate(max_enumerate = 30))
    assert len(twlist) == 30
    assert all(isinstance(x, int) for x in twlist)
    assert all(isinstance(x, int) for x in tw.to_set())

#-------------------------------------------------------------------------------
# ClassWrapper

def test_classwrapper():
    class Foo(object): pass
    class F1(Foo): pass
    class F2(F1): pass

    cw = ClassWrapper(Foo)
    
    assert cw.size() == 3

    for k in range(SAMPLES):
        item = cw.sample()
        assert cw.hasmember(item)

    cwset = cw.to_set()
    assert len(cwset) >= 3
    assert Foo in cwset
    assert F1 in cwset
    assert F2 in cwset

    cwlist = list(cw.enumerate(max_enumerate = 2))
    assert len(cwlist) == 2
    assert all(issubclass(x, Foo) for x in cwlist)
    assert all(issubclass(x, Foo) for x in cw.to_set())

#-------------------------------------------------------------------------------
# Empty

def test_empty():
    e = Empty()
    s = SetWrapper([1, 2, 3])
    
    assert e.size() == 0

    assert e.issubset(s)
    assert e.issubset(e)
    
    assert not e.issuperset(s)
    assert e.issuperset(e)
    assert e.issuperset(SetWrapper([]))

    assert not e.hasmember(rand_int())
    
    assert not e.overlaps(s)
    assert not e.overlaps(e)

    assert list(e.enumerate()) == []
    assert e.to_set() == set()


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
