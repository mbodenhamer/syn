from nose.tools import assert_raises
from syn.types.a import Type

#-------------------------------------------------------------------------------
# Type

def test_type():
    t = Type(1)
    assert t.obj == 1
    assert t.istr() == '1'
    assert t.hashable() is t.obj

    t = Type({})
    assert_raises(NotImplementedError, t.hashable)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
