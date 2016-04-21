from syn.five import STR, strf, PY2, PY3

#-------------------------------------------------------------------------------
# STR

def test_str():
    if PY2:
        assert isinstance('abc', STR)
        assert isinstance(u'abc', STR)
        assert isinstance(b'abc', STR)

    if PY3:
        assert isinstance('abc', STR)
        assert isinstance(u'abc', STR)
        assert not isinstance(b'abc', STR)

#-------------------------------------------------------------------------------
# strf

def test_strf():
    if PY2:
        assert strf(1) == u'1'

    if PY3:
        assert strf(1) == '1'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
