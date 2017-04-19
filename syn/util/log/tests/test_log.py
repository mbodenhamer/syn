import syn.util.log as log
import syn.util.log.b as blog

#-------------------------------------------------------------------------------
# Imports

def test_imports():
    assert log.Event is blog.Event
    assert log.Logger is blog.Logger

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
