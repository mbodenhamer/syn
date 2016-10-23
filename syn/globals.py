import os
import logging

#-------------------------------------------------------------------------------
# Loggers

# For messages relating to the tests
test_logger = logging.getLogger('syn tests')
_test_logger_handler = logging.StreamHandler()
_test_logger_handler.setFormatter(logging.Formatter(
    '[%(name)s][%(levelname)s] %(message)s'))
test_logger.addHandler(_test_logger_handler)
test_logger.setLevel(logging.WARNING)

#-------------------------------------------------------------------------------
# Values

SAMPLES = int(os.environ.get('SYN_TEST_SAMPLES', 10))

#-------------------------------------------------------------------------------
# Value checks

if SAMPLES <= 0:
    test_logger.warning('SAMPLES set to value <= 0 ({}) in syn.globals'
                        .format(SAMPLES)) # pragma: no cover

#-------------------------------------------------------------------------------
