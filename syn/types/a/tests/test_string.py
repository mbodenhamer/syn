#-------------------------------------------------------------------------------
# BaseString

def test_basestring():
    pass

#-------------------------------------------------------------------------------
# String

def test_string():
    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
