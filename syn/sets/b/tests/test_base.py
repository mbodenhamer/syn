from nose.tools import assert_raises
from syn.sets.b import SetNode, SetWrapper

#-------------------------------------------------------------------------------
# SetNode

def test_setnode():
    obj = SetNode([1,2,3])
    assert isinstance(obj[0], SetWrapper)
    assert obj[0].set == {1, 2, 3}

    assert_raises(NotImplementedError, obj.size)
    assert_raises(NotImplementedError, obj.union)
    assert_raises(NotImplementedError, obj.intersection)
    assert_raises(NotImplementedError, obj.difference, None)
    assert_raises(NotImplementedError, obj.complement, None)
    assert_raises(NotImplementedError, obj.issubset, None)
    assert_raises(NotImplementedError, obj.issuperset, None)
    assert_raises(NotImplementedError, obj.hasmember, None)
    assert_raises(NotImplementedError, obj.simplify)
    assert_raises(NotImplementedError, obj.sample)
    assert_raises(NotImplementedError, obj.enumerate)
    assert_raises(NotImplementedError, obj.to_set)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
