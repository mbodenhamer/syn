from nose.tools import assert_raises
from syn.util.log.b import Event, Logger

#-------------------------------------------------------------------------------
# Event

def test_event():
    Event()

#-------------------------------------------------------------------------------
# Logger

def test_logger():
    Logger

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
