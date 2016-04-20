from nose.tools import assert_raises
from syn.base.b import Base, Attr
from syn.base_utils import assert_equivalent, assert_pickle_idempotent, \
    assert_deepcopy_idempotent, assert_inequivalent

#-------------------------------------------------------------------------------
# Test basic functionality

def test_base():
    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
