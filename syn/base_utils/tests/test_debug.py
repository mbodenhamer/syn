from nose.tools import assert_raises

#-------------------------------------------------------------------------------
# Trace

def test_trace():
    from syn.base_utils import Trace

    t = Trace()
    assert_raises(NotImplementedError, t, None, 'c_call', None)
    assert_raises(NotImplementedError, t, None, 'c_exception', None)
    assert_raises(NotImplementedError, t, None, 'c_return', None)
    assert_raises(NotImplementedError, t, None, 'call', None)
    assert_raises(NotImplementedError, t, None, 'exception', None)
    assert_raises(NotImplementedError, t, None, 'line', None)
    assert_raises(NotImplementedError, t, None, 'return', None)
    assert_raises(RuntimeError, t, None, 'foo', None)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
