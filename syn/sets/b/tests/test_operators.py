from nose.tools import assert_raises
from syn.sets.b import Union, SetWrapper, Range, NULL

SAMPLES = 10

#-------------------------------------------------------------------------------
# Union

def test_union():
    u = Union({1, 2, 3}, {3, 4, 5})
    assert u._children == [SetWrapper({1, 2, 3}), SetWrapper({3, 4, 5})]
    assert set(u.enumerate()) == {1, 2, 3, 4, 5}

    assert u.hasmember(1)
    assert u.hasmember(5)
    assert not u.hasmember(6)

    for k in range(SAMPLES):
        item = u.sample()
        assert u.hasmember(item)

    assert u.to_set() == {1, 2, 3, 4, 5}

    u2 = Union(Range(1, 3), Range(5, 7), Range(6, 9), NULL, {10, 11}, {13})
    #import ipdb; ipdb.set_trace()
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

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
