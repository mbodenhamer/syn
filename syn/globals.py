import os
import logging

#-------------------------------------------------------------------------------
# Loggers

test_logger = logging.getLogger('syn tests')
_test_logger_handler = logging.StreamHandler()
_test_logger_handler.setFormatter(logging.Formatter(
    '[%(name)s][%(levelname)s] %(message)s'))
test_logger.addHandler(_test_logger_handler)
test_logger.setLevel(logging.WARNING)

#-------------------------------------------------------------------------------
# Values

SAMPLES = os.environ.get('SYN_SAMPLES', 10)

#-------------------------------------------------------------------------------
