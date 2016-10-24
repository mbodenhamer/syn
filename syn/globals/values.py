import os
from .loggers import test_logger

#-------------------------------------------------------------------------------
# Test-related

_test_samples = 10
TEST_SAMPLES = _test_samples

_suppress_test_errors = False
SUPPRESS_TEST_ERRORS = _suppress_test_errors

#-------------------------------------------------------------------------------
# Utilities

def set_values():
    global TEST_SAMPLES
    TEST_SAMPLES = int(os.environ.get('SYN_TEST_SAMPLES', _test_samples))

    global SUPPRESS_TEST_ERRORS
    SUPPRESS_TEST_ERRORS = bool(int(os.environ.get('SYN_SUPPRESS_TEST_ERRORS', 
                                                   _suppress_test_errors)))

def check_values():
    if TEST_SAMPLES <= 0:
        test_logger.warning('TEST_SAMPLES set to value <= 0 ({}) in syn.globals'
                            .format(TEST_SAMPLES))

#-------------------------------------------------------------------------------

set_values()
check_values()

#-------------------------------------------------------------------------------
# __all__

__all__ = ('TEST_SAMPLES', 'SUPPRESS_TEST_ERRORS')

#-------------------------------------------------------------------------------
