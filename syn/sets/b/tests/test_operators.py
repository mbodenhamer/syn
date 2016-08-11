from nose.tools import assert_raises
from syn.five import xrange
from syn.base_utils import feq
from syn.sets.b import Union, SetWrapper, Range, NULL, Intersection, \
    Difference, ClassWrapper, Product

SAMPLES = 10
range = lambda *args: list(xrange(*args))

#-------------------------------------------------------------------------------
# Union

def test_union():
    u = Union({1, 2, 3}, {3, 4, 5})
    assert u._children == [SetWrapper({1, 2, 3}), SetWrapper({3, 4, 5})]
    assert set(u.enumerate()) == {1, 2, 3, 4, 5}
    assert set(u.enumerate(lazy=True)) == {1, 2, 3, 4, 5}

    assert u.size() == 5
    assert u.size_limits() == (3, 6)
    assert feq(u.expected_size(), 4.5)

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

    # Sanity Check
    class Foo(object): pass
    class F1(Foo): pass
    u = Union(range(10), Range(10, 20), ClassWrapper(Foo))
    assert u.size() == 23
    assert feq(u.expected_size(), 17)
    us = u.to_set()
    assert len(us) == 23
    assert us == set(range(10)) | set(range(10, 21)) | set([Foo, F1])

    # Edge Cases
    assert list(Union().enumerate()) == []
    assert Union().to_set() == set()
    assert Union(Range(1, 2)).to_set() == {1, 2}
    assert Union({2, 4}).to_set() == {2, 4}
    
#-------------------------------------------------------------------------------
# Intersection

def test_intersection():
    i = Intersection({1, 2, 3}, {2, 3, 4})
    assert i._children == [SetWrapper({1, 2, 3}), SetWrapper({2, 3, 4})]
    assert set(i.enumerate()) == {2, 3}
    assert set(i.lazy_enumerate()) == {2, 3}

    assert i.size() == 2
    assert i.size_limits() == (0, 3)

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

    i3 = Intersection({1, 2, 3}, {1, 2, 3})
    assert len(list(i3.enumerate(max_enumerate = 2))) == 2

    i4 = Intersection({1, 2}, {3, 4})
    assert i4.to_set() == set()
    assert_raises(ValueError, i4.lazy_sample)

    # Advantages of lazy_enumerate()
    i5 = Intersection(Range(-10000000000, 10000000000), range(10))
    assert set(i5.lazy_enumerate()) == set(range(10))

    # Test max_enumerate
    i6 = Intersection(Range(0, 100), Range(10, 90))
    assert list(i6.lazy_enumerate(max_enumerate=10)) == range(10, 20)

    # Sanity check
    i7 = Intersection(range(10), Range(0, 50))
    assert i7.to_set() == set(range(10))

    # Edge Cases
    assert Intersection().to_set() == set()
    assert list(Intersection().lazy_enumerate()) == []
    assert Intersection(Range(1, 5)).to_set() == set(range(1,6))

#-------------------------------------------------------------------------------
# Difference

def test_difference():
    d = Difference({1, 2, 3}, {2, 3, 4})
    assert d._children == [SetWrapper({1, 2, 3}), SetWrapper({2, 3, 4})]
    assert set(d.enumerate()) == {1}
    assert set(d.lazy_enumerate()) == {1}
    
    assert d.size() == 1
    assert d.size_limits() == (0, 3)
    assert Difference({1, 2}, {1, 2, 3}).size_limits() == (0, 2)

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

    # Test lazy_enumerate
    d = Difference(Range(0, 100000), Range(100, 200))
    assert list(d.lazy_enumerate(max_enumerate=10)) == range(10)

#-------------------------------------------------------------------------------
# Product

def test_product():
    p = Product(Range(1, 5), Range(6, 10), Range(11, 15))
    ps = p.to_set()
    assert (1, 6, 11) in ps
    assert (5, 6, 11) in ps
    assert (5, 10, 11) in ps
    assert (5, 10, 15) in ps

    assert feq(p.expected_size(), 125)

    assert not p.hasmember((0, 6, 11))
    for k in range(SAMPLES):
        item = p.sample()
        assert p.hasmember(item)

    p = Product({1}, {2}, {3})
    assert p.to_set() == set([(1, 2, 3)])
    assert p.sample() == (1, 2, 3)

#-------------------------------------------------------------------------------
# Combined Operators

def test_combined_operators():
    s = Union(Union(range(5), Range(5, 9)),
              Union(Range(10, 14), range(15, 20)))

    assert list(sorted(s.lazy_enumerate())) == range(20)
    assert s.to_set() == set(range(20))

    s = Intersection(Union(Range(-10, 0),
                           Intersection(Range(0, 10), Range(0, 20))),
                     Difference(Range(0, 10), Range(5, 100000)))
    assert s.to_set() == set(range(5))
    assert list(sorted(s.lazy_enumerate())) == range(5)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
