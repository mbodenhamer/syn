import logging

#-------------------------------------------------------------------------------
# For messages relating to the tests

test_logger = logging.getLogger('syn tests')
_test_logger_handler = logging.StreamHandler()
_test_logger_handler.setFormatter(logging.Formatter(
    '[%(name)s][%(levelname)s] %(message)s'))
test_logger.addHandler(_test_logger_handler)
test_logger.setLevel(logging.WARNING)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('test_logger',)

#-------------------------------------------------------------------------------
