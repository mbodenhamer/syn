import os
import random
from six import PY3
from .loggers import test_logger

#-------------------------------------------------------------------------------
# Test-related

_test_samples = 10
TEST_SAMPLES = _test_samples

_suppress_test_errors = False
SUPPRESS_TEST_ERRORS = _suppress_test_errors

_random_seed = -1
RANDOM_SEED = _random_seed

#-------------------------------------------------------------------------------
# Utilities

def set_values():
    global TEST_SAMPLES
    TEST_SAMPLES = int(os.environ.get('SYN_TEST_SAMPLES', _test_samples))

    global SUPPRESS_TEST_ERRORS
    SUPPRESS_TEST_ERRORS = bool(int(os.environ.get('SYN_SUPPRESS_TEST_ERRORS', 
                                                   _suppress_test_errors)))

    global RANDOM_SEED
    RANDOM_SEED = int(os.environ.get('SYN_RANDOM_SEED', _random_seed))

    if RANDOM_SEED >= 0:
        if PY3:
            random.seed(RANDOM_SEED, version=1)
        else:
            random.seed(RANDOM_SEED)

def check_values():
    if TEST_SAMPLES <= 0:
        test_logger.warning('TEST_SAMPLES set to value <= 0 ({}) in syn.globals'
                            .format(TEST_SAMPLES))

#-------------------------------------------------------------------------------

set_values()
check_values()

#-------------------------------------------------------------------------------
# __all__

__all__ = ('TEST_SAMPLES', 'SUPPRESS_TEST_ERRORS', 'RANDOM_SEED')

#-------------------------------------------------------------------------------
