from syn.types.a import Type

#-------------------------------------------------------------------------------
# Type

def test_type():
    t = Type(1)
    assert t.istr() == '1'
    t.hashable()

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
