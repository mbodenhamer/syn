from syn.five import NUM, PY2

#-------------------------------------------------------------------------------
# NUM

def test_num():
    if PY2:
        assert NUM == (float, int, long)

    else:
        assert NUM == (float, int)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
