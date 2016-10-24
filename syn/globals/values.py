import os
from .loggers import test_logger

#-------------------------------------------------------------------------------
# Test-related

_samples = 10
SAMPLES = _samples

_suppress_test_errors = False
SUPPRESS_TEST_ERRORS = _suppress_test_errors

#-------------------------------------------------------------------------------
# Utilities

def set_values():
    global SAMPLES
    SAMPLES = int(os.environ.get('SYN_TEST_SAMPLES', _samples))

    global SUPPRESS_TEST_ERRORS
    SUPPRESS_TEST_ERRORS = bool(int(os.environ.get('SYN_SUPPRESS_TEST_ERRORS', 
                                                   _suppress_test_errors)))

def check_values():
    if SAMPLES <= 0:
        test_logger.warning('SAMPLES set to value <= 0 ({}) in syn.globals'
                            .format(SAMPLES))

#-------------------------------------------------------------------------------

set_values()
check_values()

#-------------------------------------------------------------------------------
# __all__

__all__ = ('SAMPLES', 'SUPPRESS_TEST_ERRORS')

#-------------------------------------------------------------------------------
