import syn.util
import syn.util.constraint as con
import syn.util.log as log

#-------------------------------------------------------------------------------
# Test Imports

def test_imports():
    assert syn.util.constraint is con
    assert syn.util.log is log

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
