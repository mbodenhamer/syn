import os
from .loggers import test_logger

#-------------------------------------------------------------------------------
# Test-related

SAMPLES = 10

#-------------------------------------------------------------------------------
# Utilities

def set_values():
    global SAMPLES
    SAMPLES = int(os.environ.get('SYN_TEST_SAMPLES', 10))

def check_values():
    if SAMPLES <= 0:
        test_logger.warning('SAMPLES set to value <= 0 ({}) in syn.globals'
                            .format(SAMPLES))

#-------------------------------------------------------------------------------

set_values()
check_values()

#-------------------------------------------------------------------------------
# __all__

__all__ = ('SAMPLES',)

#-------------------------------------------------------------------------------
