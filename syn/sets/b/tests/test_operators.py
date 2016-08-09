from nose.tools import assert_raises
from syn.five import xrange
from syn.sets.b import Union, SetWrapper, Range, NULL, Intersection, \
    Difference, StrRange, Complement
from syn.sets.b.base import Args

SAMPLES = 10
range = lambda *args: list(xrange(*args))

#-------------------------------------------------------------------------------
# Union

def test_union():
    u = Union({1, 2, 3}, {3, 4, 5})
    assert u._children == [SetWrapper({1, 2, 3}), SetWrapper({3, 4, 5})]
    assert set(u.enumerate()) == {1, 2, 3, 4, 5}
    assert set(u.enumerate(lazy=True)) == {1, 2, 3, 4, 5}

    assert u.hasmember(1)
    assert u.hasmember(5)
    assert not u.hasmember(6)

    for k in range(SAMPLES):
        item = u.sample()
        assert u.hasmember(item)

    item = u.sample(lazy=True)
    assert u.hasmember(item)

    assert u.to_set() == {1, 2, 3, 4, 5}

    u2 = Union(Range(1, 3), Range(5, 7), Range(6, 9), NULL, {10, 11}, {13})
    assert u2.to_set() == {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13}
    assert sorted(u2.enumerate()) == [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13]
    assert len(list(u2.enumerate(max_enumerate = 2))) == 2

    for k in range(SAMPLES):
        item = u2.sample()
        assert u2.hasmember(item)

    # NOTE: these are not valid Union objects
    assert Union(Range(1, 2)).to_set() == {1, 2}
    assert Union({2, 4}).to_set() == {2, 4}
    

#-------------------------------------------------------------------------------
# Intersection

def test_intersection():
    i = Intersection({1, 2, 3}, {2, 3, 4})
    assert i._children == [SetWrapper({1, 2, 3}), SetWrapper({2, 3, 4})]
    assert set(i.enumerate()) == {2, 3}
    assert set(i.lazy_enumerate()) == {2, 3}

    assert not i.hasmember(1)
    assert i.hasmember(2)
    assert not i.hasmember(4)

    for k in range(SAMPLES):
        item = i.sample()
        assert i.hasmember(item)
    
    item = i.lazy_sample()
    assert i.hasmember(item)
    item = i.get_one()
    assert i.hasmember(item)

    assert i.to_set() == {2, 3}

    assert Intersection({1, 2}, NULL).to_set() == set()

    i2 = Intersection(range(10), range(8), Range(2, 7), Range(3, 8))
    assert i2.to_set() == set(range(3,8))
    assert sorted(list(i2.enumerate())) == range(3, 8)
    assert sorted(list(i2.enumerate(lazy=True))) == range(3, 8)

    for k in range(SAMPLES):
        item = i2.sample()
        assert i2.hasmember(item)

    assert Intersection(Range(1, 5), Range(2, 6)).to_set() == {2, 3, 4, 5}
    assert Intersection(Range(1, 5), {2, 3}).to_set() == {2, 3}
    assert Intersection(Range(1, 5), Union({2}, Range(4,5))).to_set() == {2, 4, 5}
    assert Intersection(NULL, Union({2}, Range(4,5))).to_set() == set()

    # NOTE: this is not a valid Intersection object
    assert Intersection(Range(1, 5)).to_set() == set(range(1,6))

    i3 = Intersection({1, 2, 3}, {1, 2, 3})
    assert len(list(i3.enumerate(max_enumerate = 2))) == 2

    i4 = Intersection({1, 2}, {3, 4})
    assert i4.to_set() == set()
    assert_raises(ValueError, i4.lazy_sample)


#-------------------------------------------------------------------------------
# Difference

def test_difference():
    d = Difference({1, 2, 3}, {2, 3, 4})
    assert d._children == [SetWrapper({1, 2, 3}), SetWrapper({2, 3, 4})]
    assert set(d.enumerate()) == {1}
    assert set(d.lazy_enumerate()) == {1}
    
    assert d.hasmember(1)
    assert not d.hasmember(2)
    assert not d.hasmember(4)

    for k in range(SAMPLES):
        item = d.sample()
        assert d.hasmember(item)
    
    item = d.lazy_sample()
    assert d.hasmember(item)

    assert d.to_set() == {1}

    d = Difference(Range(1, 5), Range(2, 3))
    assert d.to_set() == {1, 4, 5}

    d = Difference(Range(1, 5), Range(3, 7))
    assert d.to_set() == {1, 2}

    d = Difference(Range(1, 5), {4, 5, 6})
    assert d.to_set() == {1, 2, 3}

    d = Difference({1, 2}, {1, 2, 3})
    assert d.to_set() == set()
    assert_raises(ValueError, d.lazy_sample)

#-------------------------------------------------------------------------------
# Complement

def test_complement():
    c = Complement([1, 2, 3])

    assert c.hasmember(4)
    assert not c.hasmember(1)
    assert c.to_set() == set()
    assert c.to_set(universe = set(range(5))) == {0, 4}
    
    c = Complement(Union([1], [2, 3]))

    assert c.hasmember(4)
    assert not c.hasmember(1)
    assert c.to_set() == set()
    assert c.to_set(universe = SetWrapper(range(5))) == {0, 4}

    U = SetWrapper(range(10))
    assert sorted(c.lazy_enumerate(universe=U)) == [0] + range(4, 10)
    assert sorted(c.enumerate(universe=U)) == [0] + range(4, 10)
    item = c.lazy_sample(universe=U)
    assert c.hasmember(item)
    item = c.sample(universe=U)
    assert c.hasmember(item)

    r = Range(1, 4)
    rc = Complement(r)
    assert rc.hasmember(0)
    assert not rc.hasmember(1)
    assert not rc.hasmember(4)
    assert rc.hasmember(5)

    assert len(rc.to_set()) == Args._attrs['max_enumerate'].default

    from syn.sets.b.range import ASCII
    r = StrRange(97, 98)
    rc = Complement(r)
    assert len(rc.to_set()) == ASCII.ub - ASCII.lb - 1

    c = Complement([1, 2])
    assert c.to_set(universe=SetWrapper({1, 2})) == set()
    assert_raises(ValueError, c.lazy_sample, universe=SetWrapper({1, 2}))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
