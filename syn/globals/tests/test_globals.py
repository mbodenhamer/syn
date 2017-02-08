import os
from syn.base_utils import assign, setitem
import syn.globals.values as gv

#-------------------------------------------------------------------------------
# values

def test_values():
    msgs = []
    class FakeLogger(object):
        def warning(self, msg):
            msgs.append(msg)

    logger = FakeLogger()
    samples = gv.TEST_SAMPLES
    suppress = gv.SUPPRESS_TEST_ERRORS

    try:
        with setitem(os.environ, 'SYN_TEST_SAMPLES', '0'):
            gv.set_values()
            assert gv.TEST_SAMPLES == 0

            with assign(gv, 'test_logger', logger):
                gv.check_values()
                assert msgs[-1] == 'TEST_SAMPLES set to value <= 0 (0) in syn.globals'

        with setitem(os.environ, 'SYN_SUPPRESS_TEST_ERRORS', '0'):
            gv.set_values()
            assert gv.SUPPRESS_TEST_ERRORS is False

        with setitem(os.environ, 'SYN_SUPPRESS_TEST_ERRORS', '1'):
            gv.set_values()
            assert gv.SUPPRESS_TEST_ERRORS is True

    finally:
        gv.set_values()

    assert gv.TEST_SAMPLES == samples
    assert gv.SUPPRESS_TEST_ERRORS == suppress

    # Uncomment for a system-dependent sanity check

    # import random
    # rv = random.randint(1, 100000000) 
    # if gv.RANDOM_SEED >= 0:
    #     assert rv == 13436425
    # else:
    #     # This should not fail, statistically speaking
    #     assert rv != 13436425

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
